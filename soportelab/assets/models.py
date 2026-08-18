from django.conf import settings
from django.db import models
from django.urls import reverse


class Asset(models.Model):
    class AssetType(models.TextChoices):
        DESKTOP = "desktop", "PC de escritorio"
        LAPTOP = "laptop", "Notebook"
        PRINTER = "printer", "Impresora"
        NETWORK = "network", "Equipo de red"
        MOBILE = "mobile", "Dispositivo móvil"
        OTHER = "other", "Otro"

    class Status(models.TextChoices):
        ACTIVE = "active", "Activo"
        MAINTENANCE = "maintenance", "En mantenimiento"
        RETIRED = "retired", "Retirado"

    asset_tag = models.CharField("código de activo", max_length=30, unique=True)
    name = models.CharField("nombre", max_length=120)
    asset_type = models.CharField(
        "tipo", max_length=20, choices=AssetType.choices, default=AssetType.DESKTOP
    )
    brand = models.CharField("marca", max_length=80, blank=True)
    model = models.CharField("modelo", max_length=100, blank=True)
    serial_number = models.CharField("número de serie", max_length=100, blank=True)
    status = models.CharField(
        "estado", max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="asignado a",
        related_name="assigned_assets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.CharField("ubicación", max_length=120, blank=True)
    operating_system = models.CharField("sistema operativo", max_length=120, blank=True)
    notes = models.TextField("notas", blank=True)
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        ordering = ("asset_tag",)
        verbose_name = "activo"
        verbose_name_plural = "activos"

    def __str__(self):
        return f"{self.asset_tag} · {self.name}"

    @property
    def code(self):
        """UI-friendly alias kept for template readability."""
        return self.asset_tag

    def get_absolute_url(self):
        return reverse("assets:detail", kwargs={"pk": self.pk})
