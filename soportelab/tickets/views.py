from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import StaffRequiredMixin

from .forms import TicketCommentForm, TicketCreateForm, TicketStatusForm, TicketUpdateForm
from .models import Ticket, TicketActivity


class VisibleTicketMixin:
    def get_queryset(self):
        return (
            Ticket.objects.visible_to(self.request.user)
            .select_related("category", "requester", "assignee", "asset")
            .prefetch_related("activities__author")
        )


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 20

    def get_queryset(self):
        queryset = Ticket.objects.visible_to(self.request.user).select_related(
            "category", "requester", "assignee", "asset"
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(code__icontains=query) | Q(title__icontains=query) | Q(description__icontains=query)
            )
        for field in ("status", "priority"):
            value = self.request.GET.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        for field in ("category", "assignee"):
            value = self.request.GET.get(field)
            if value and value.isdigit():
                queryset = queryset.filter(**{f"{field}_id": value})
        if self.request.GET.get("overdue") == "1":
            from django.utils import timezone

            queryset = queryset.active().filter(due_at__lt=timezone.now())
        return queryset


class TicketDetailView(LoginRequiredMixin, VisibleTicketMixin, DetailView):
    model = Ticket
    template_name = "tickets/ticket_detail.html"
    context_object_name = "ticket"
    slug_field = "code"
    slug_url_kwarg = "code"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = TicketCommentForm()
        context["status_form"] = TicketStatusForm(ticket=self.object)
        context["events"] = self.object.activities.select_related("author")
        return context


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketCreateForm
    template_name = "tickets/ticket_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.requester = self.request.user
        response = super().form_valid(form)
        TicketActivity.objects.create(
            ticket=self.object,
            author=self.request.user,
            activity_type=TicketActivity.ActivityType.COMMENT,
            message="Ticket creado",
        )
        messages.success(self.request, f"Se creó el ticket {self.object.code}.")
        return response


class TicketUpdateView(LoginRequiredMixin, StaffRequiredMixin, VisibleTicketMixin, UpdateView):
    model = Ticket
    form_class = TicketUpdateForm
    template_name = "tickets/ticket_form.html"
    slug_field = "code"
    slug_url_kwarg = "code"

    def form_valid(self, form):
        old_assignee_id = Ticket.objects.values_list("assignee_id", flat=True).get(pk=self.object.pk)
        if form.instance.assignee_id and not old_assignee_id and form.instance.status == Ticket.Status.OPEN:
            form.instance.status = Ticket.Status.ASSIGNED
        response = super().form_valid(form)
        if old_assignee_id != self.object.assignee_id:
            TicketActivity.objects.create(
                ticket=self.object,
                author=self.request.user,
                activity_type=TicketActivity.ActivityType.ASSIGNMENT,
                message="Responsable actualizado",
                old_value=str(old_assignee_id or "Sin asignar"),
                new_value=str(self.object.assignee or "Sin asignar"),
            )
        messages.success(self.request, "Ticket actualizado.")
        return response


class TicketStatusView(LoginRequiredMixin, View):
    def post(self, request, code=None, pk=None):
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo el personal de soporte puede cambiar estados.")
        lookup = {"pk": pk} if pk is not None else {"code": code}
        ticket = get_object_or_404(Ticket.objects.visible_to(request.user), **lookup)
        form = TicketStatusForm(request.POST, ticket=ticket)
        if form.is_valid():
            ticket.diagnosis = form.cleaned_data["diagnosis"]
            ticket.root_cause = form.cleaned_data["root_cause"]
            ticket.resolution = form.cleaned_data["resolution"]
            ticket.transition_to(
                form.cleaned_data["status"], request.user, form.cleaned_data["message"]
            )
            messages.success(request, "Estado actualizado.")
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
        return redirect(ticket)


class TicketCommentView(LoginRequiredMixin, View):
    def post(self, request, code=None, pk=None):
        lookup = {"pk": pk} if pk is not None else {"code": code}
        ticket = get_object_or_404(Ticket.objects.visible_to(request.user), **lookup)
        data = request.POST.copy()
        if "message" not in data and "body" in data:
            data["message"] = data["body"]
        form = TicketCommentForm(data)
        if form.is_valid():
            TicketActivity.objects.create(
                ticket=ticket,
                author=request.user,
                activity_type=TicketActivity.ActivityType.COMMENT,
                message=form.cleaned_data["message"],
                is_internal=request.user.is_staff and "is_internal" in request.POST,
            )
            messages.success(request, "Comentario agregado.")
        return redirect(ticket)


class TicketResolveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo el personal de soporte puede resolver tickets.")
        ticket = get_object_or_404(Ticket.objects.visible_to(request.user), pk=pk)
        resolution = request.POST.get("resolution", "").strip()
        if not resolution:
            messages.error(request, "La resolución es obligatoria.")
            return redirect(ticket)
        ticket.root_cause = request.POST.get("root_cause", "").strip()
        ticket.resolution = resolution
        ticket.diagnosis = ticket.diagnosis or ticket.root_cause or resolution
        ticket.transition_to(Ticket.Status.RESOLVED, request.user, "Ticket resuelto")
        messages.success(request, "Ticket resuelto.")
        return redirect(ticket)
