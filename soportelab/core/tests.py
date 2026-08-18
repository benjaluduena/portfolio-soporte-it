from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from tickets.models import Category, Ticket

from .views import DashboardView, ReportsView


class CoreMetricsTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.staff = users.objects.create_user(username="staff", is_staff=True)
        self.category = Category.objects.create(name="Hardware")
        self.open_ticket = Ticket.objects.create(
            title="Monitor sin señal",
            description="Pantalla negra",
            category=self.category,
            requester=self.staff,
            priority=Ticket.Priority.CRITICAL,
        )
        self.open_ticket.due_at = timezone.now() - timezone.timedelta(hours=1)
        self.open_ticket.save(update_fields=("due_at",))
        self.resolved_ticket = Ticket.objects.create(
            title="Mouse desconectado",
            description="No responde",
            category=self.category,
            requester=self.staff,
            diagnosis="Cable desconectado",
            resolution="Se conectó el cable",
        )
        self.resolved_ticket.transition_to(Ticket.Status.RESOLVED, self.staff)

    def context_for(self, view_class):
        view = view_class()
        view.request = RequestFactory().get("/")
        view.request.user = self.staff
        view.kwargs = {}
        return view.get_context_data()

    def test_dashboard_operational_metrics(self):
        context = self.context_for(DashboardView)
        self.assertEqual(context["open_count"], 1)
        self.assertEqual(context["critical_count"], 1)
        self.assertEqual(context["overdue_count"], 1)
        self.assertEqual(context["resolved_this_month"], 1)

    def test_reports_include_sla_and_breakdowns(self):
        context = self.context_for(ReportsView)
        self.assertEqual(context["total_tickets"], 2)
        sla = {item["status"]: item["total"] for item in context["sla_metrics"]}
        self.assertEqual(sla["breached"], 1)
        self.assertEqual(sla["met"], 1)
        self.assertEqual(sum(item["total"] for item in context["status_metrics"]), 2)

    def test_main_server_rendered_pages_load(self):
        from assets.models import Asset
        from knowledge.models import KnowledgeArticle

        asset = Asset.objects.create(asset_tag="MON-001", name="Monitor demo")
        article = KnowledgeArticle.objects.create(
            title="Revisar cable de video",
            slug="revisar-cable-video",
            summary="Diagnóstico inicial",
            content="Verificar conexión y probar otro puerto.",
            status=KnowledgeArticle.Status.PUBLISHED,
            author=self.staff,
        )
        self.client.force_login(self.staff)
        urls = (
            reverse("core:dashboard"),
            reverse("tickets:list"),
            reverse("tickets:detail", kwargs={"pk": self.open_ticket.pk}),
            reverse("assets:list"),
            reverse("assets:detail", kwargs={"pk": asset.pk}),
            reverse("knowledge:list"),
            reverse("knowledge:detail", kwargs={"pk": article.pk}),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
