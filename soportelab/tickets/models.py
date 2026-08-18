from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator


class Category(models.Model):
    name = models.CharField("nombre", max_length=80, unique=True)
    description = models.TextField("descripción", blank=True)
    is_active = models.BooleanField("activa", default=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.name


class TicketQuerySet(models.QuerySet):
    def visible_to(self, user):
        if not user.is_authenticated:
            return self.none()
        if user.is_staff:
            return self
        return self.filter(requester=user)

    def active(self):
        return self.exclude(status__in=(Ticket.Status.RESOLVED, Ticket.Status.CLOSED))


class Ticket(models.Model):
    class TicketType(models.TextChoices):
        INCIDENT = "incident", "Incidente"
        REQUEST = "request", "Solicitud"

    class Priority(models.TextChoices):
        LOW = "low", "Baja"
        MEDIUM = "medium", "Media"
        HIGH = "high", "Alta"
        CRITICAL = "critical", "Crítica"

    class Status(models.TextChoices):
        OPEN = "open", "Abierto"
        ASSIGNED = "assigned", "Asignado"
        IN_PROGRESS = "in_progress", "En progreso"
        PENDING = "pending", "Pendiente"
        RESOLVED = "resolved", "Resuelto"
        CLOSED = "closed", "Cerrado"

    SLA_HOURS = {
        Priority.LOW: 72,
        Priority.MEDIUM: 48,
        Priority.HIGH: 24,
        Priority.CRITICAL: 8,
    }

    code = models.CharField("código", max_length=20, unique=True, editable=False)
    title = models.CharField("título", max_length=160)
    description = models.TextField("descripción")
    ticket_type = models.CharField(
        "tipo", max_length=20, choices=TicketType.choices, default=TicketType.INCIDENT
    )
    category = models.ForeignKey(
        Category, verbose_name="categoría", related_name="tickets", on_delete=models.PROTECT
    )
    priority = models.CharField(
        "prioridad", max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        "estado", max_length=20, choices=Status.choices, default=Status.OPEN
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="solicitante",
        related_name="requested_tickets",
        on_delete=models.PROTECT,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="responsable",
        related_name="assigned_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
    )
    asset = models.ForeignKey(
        "assets.Asset",
        verbose_name="activo afectado",
        related_name="tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    diagnosis = models.TextField("diagnóstico", blank=True)
    root_cause = models.TextField("causa raíz", blank=True)
    resolution = models.TextField("resolución", blank=True)
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)
    due_at = models.DateTimeField("vencimiento SLA", editable=False)
    resolved_at = models.DateTimeField("resuelto", null=True, blank=True, editable=False)
    closed_at = models.DateTimeField("cerrado", null=True, blank=True, editable=False)

    objects = TicketQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "priority")),
            models.Index(fields=("due_at",)),
        ]
        verbose_name = "ticket"
        verbose_name_plural = "tickets"

    def __str__(self):
        return f"{self.code} · {self.title}"

    def get_absolute_url(self):
        return reverse("tickets:detail", kwargs={"pk": self.pk})

    @property
    def assigned_to(self):
        """Compatibility alias used by the presentation layer."""
        return self.assignee

    @property
    def impact(self):
        return {
            self.Priority.LOW: "Bajo",
            self.Priority.MEDIUM: "Medio",
            self.Priority.HIGH: "Alto",
            self.Priority.CRITICAL: "Generalizado",
        }[self.priority]

    @property
    def urgency(self):
        return self.get_priority_display()

    @property
    def is_overdue(self):
        return self.status not in (self.Status.RESOLVED, self.Status.CLOSED) and self.due_at < timezone.now()

    @property
    def sla_status(self):
        if self.status in (self.Status.RESOLVED, self.Status.CLOSED):
            endpoint = self.resolved_at or self.closed_at
            return "met" if endpoint and endpoint <= self.due_at else "breached"
        return "breached" if self.is_overdue else "on_time"

    @property
    def resolution_time(self):
        if not self.resolved_at:
            return None
        return self.resolved_at - self.created_at

    def clean(self):
        super().clean()
        if self.status in (self.Status.RESOLVED, self.Status.CLOSED):
            errors = {}
            if not self.diagnosis.strip():
                errors["diagnosis"] = "El diagnóstico es obligatorio para resolver el ticket."
            if not self.resolution.strip():
                errors["resolution"] = "La resolución es obligatoria para resolver el ticket."
            if errors:
                raise ValidationError(errors)

    def _new_due_at(self, start=None):
        return (start or timezone.now()) + timedelta(hours=self.SLA_HOURS[self.priority])

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new and not self.due_at:
            self.due_at = self._new_due_at()
        if is_new and not self.code:
            with transaction.atomic():
                last = Ticket.objects.select_for_update().order_by("-pk").first()
                prefix = "REQ" if self.ticket_type == self.TicketType.REQUEST else "INC"
                self.code = f"{prefix}-{((last.pk if last else 0) + 1):04d}"
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def transition_to(self, new_status, author, message=""):
        if new_status not in self.Status.values:
            raise ValidationError({"status": "Estado inválido."})

        old_status = self.status
        if old_status == new_status:
            return False

        now = timezone.now()
        self.status = new_status
        if new_status == self.Status.RESOLVED:
            self.resolved_at = now
            self.closed_at = None
        elif new_status == self.Status.CLOSED:
            self.closed_at = now
            self.resolved_at = self.resolved_at or now
        elif old_status in (self.Status.RESOLVED, self.Status.CLOSED):
            self.resolved_at = None
            self.closed_at = None
            self.due_at = self._new_due_at(now)

        self.full_clean()
        self.save()
        TicketActivity.objects.create(
            ticket=self,
            author=author,
            activity_type=TicketActivity.ActivityType.STATUS_CHANGE,
            message=message or "Cambio de estado",
            old_value=old_status,
            new_value=new_status,
        )
        return True


class TicketActivity(models.Model):
    class ActivityType(models.TextChoices):
        COMMENT = "comment", "Comentario"
        STATUS_CHANGE = "status_change", "Cambio de estado"
        ASSIGNMENT = "assignment", "Asignación"
        DIAGNOSIS = "diagnosis", "Diagnóstico"

    ticket = models.ForeignKey(
        Ticket, verbose_name="ticket", related_name="activities", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="autor",
        related_name="ticket_activities",
        on_delete=models.PROTECT,
    )
    activity_type = models.CharField(
        "tipo", max_length=20, choices=ActivityType.choices, default=ActivityType.COMMENT
    )
    message = models.TextField("detalle")
    old_value = models.CharField("valor anterior", max_length=120, blank=True)
    new_value = models.CharField("valor nuevo", max_length=120, blank=True)
    is_internal = models.BooleanField("nota interna", default=False)
    created_at = models.DateTimeField("creado", auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "actividad"
        verbose_name_plural = "actividades"

    def __str__(self):
        return f"{self.ticket.code}: {Truncator(self.message).chars(50)}"

    @property
    def event_type(self):
        return self.activity_type

    @property
    def description(self):
        return self.message

    @property
    def body(self):
        return self.message

    @property
    def user(self):
        return self.author

    @property
    def icon(self):
        return "✎" if self.activity_type == self.ActivityType.COMMENT else "↻"
