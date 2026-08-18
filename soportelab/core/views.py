from collections import Counter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.utils import timezone
from django.views.generic import TemplateView

from tickets.models import Ticket, TicketActivity


def format_duration(value):
    if not value:
        return "Sin datos"
    total_minutes = round(value.total_seconds() / 60)
    days, remaining = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(remaining, 60)
    parts = []
    if days:
        parts.append(f"{days} d")
    if hours:
        parts.append(f"{hours} h")
    if minutes or not parts:
        parts.append(f"{minutes} min")
    return " ".join(parts)


class HomeView(TemplateView):
    template_name = "core/landing.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tickets = Ticket.objects.visible_to(self.request.user)
        active = tickets.active()
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        avg_resolution = tickets.filter(resolved_at__isnull=False).aggregate(
            value=Avg(
                ExpressionWrapper(F("resolved_at") - F("created_at"), output_field=DurationField())
            )
        )["value"]
        context.update(
            {
                "open_count": active.count(),
                "critical_count": active.filter(priority=Ticket.Priority.CRITICAL).count(),
                "overdue_count": active.filter(due_at__lt=timezone.now()).count(),
                "resolved_this_month": tickets.filter(resolved_at__gte=month_start).count(),
                "average_resolution_time": avg_resolution,
                "urgent_tickets": active.select_related("category", "assignee").order_by(
                    "due_at", "-priority"
                )[:5],
                "status_metrics": tickets.values("status").annotate(total=Count("id")).order_by(),
                "priority_metrics": tickets.values("priority").annotate(total=Count("id")).order_by(),
                "top_categories": tickets.values("category__name")
                .annotate(total=Count("id"))
                .order_by("-total")[:5],
                "top_assets": tickets.exclude(asset=None)
                .values("asset__asset_tag", "asset__name")
                .annotate(total=Count("id"))
                .order_by("-total")[:5],
            }
        )
        context["stats"] = {
            "open": context["open_count"],
            "new": tickets.filter(created_at__date=timezone.localdate()).count(),
            "critical": context["critical_count"],
            "resolved": context["resolved_this_month"],
            "closed": tickets.filter(status__in=(Ticket.Status.RESOLVED, Ticket.Status.CLOSED)).count(),
            "total": tickets.count(),
            "avg_resolution": format_duration(context["average_resolution_time"]),
        }
        context["attention_tickets"] = context["urgent_tickets"]
        context["recent_activity"] = (
            TicketActivity.objects.filter(ticket__in=tickets)
            .select_related("ticket", "author")
            .order_by("-created_at")[:5]
        )
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "core/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Ticket.objects.visible_to(self.request.user).select_related("category")
        tickets = list(queryset)
        sla = Counter(ticket.sla_status for ticket in tickets)
        context.update(
            {
                "total_tickets": len(tickets),
                "status_metrics": queryset.values("status").annotate(total=Count("id")).order_by(),
                "priority_metrics": queryset.values("priority").annotate(total=Count("id")).order_by(),
                "category_metrics": queryset.values("category__name")
                .annotate(total=Count("id"))
                .order_by("-total"),
                "sla_metrics": [
                    {"status": "on_time", "total": sla["on_time"]},
                    {"status": "met", "total": sla["met"]},
                    {"status": "breached", "total": sla["breached"]},
                ],
            }
        )
        return context
