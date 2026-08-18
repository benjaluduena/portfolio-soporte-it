from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from assets.models import Asset

from .forms import TicketCreateForm, TicketStatusForm
from .models import Category, Ticket, TicketActivity


class TicketModelTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.requester = users.objects.create_user(username="solicitante", password="test1234")
        self.other_user = users.objects.create_user(username="otro", password="test1234")
        self.agent = users.objects.create_user(username="tecnico", password="test1234", is_staff=True)
        self.category = Category.objects.create(name="Red")
        self.asset = Asset.objects.create(
            asset_tag="PC-001", name="PC recepción", assigned_to=self.requester
        )

    def make_ticket(self, **overrides):
        data = {
            "title": "Sin conexión",
            "description": "No navega desde esta mañana",
            "category": self.category,
            "requester": self.requester,
        }
        data.update(overrides)
        return Ticket.objects.create(**data)

    def test_generates_sequential_readable_codes(self):
        first = self.make_ticket()
        second = self.make_ticket(title="Otro incidente")
        self.assertEqual(first.code, "INC-0001")
        self.assertEqual(second.code, "INC-0002")

    def test_request_uses_request_prefix(self):
        ticket = self.make_ticket(ticket_type=Ticket.TicketType.REQUEST)
        self.assertEqual(ticket.code, "REQ-0001")

    def test_calculates_due_date_from_priority(self):
        before = timezone.now()
        ticket = self.make_ticket(priority=Ticket.Priority.CRITICAL)
        expected = before + timedelta(hours=8)
        self.assertLess(abs(ticket.due_at - expected), timedelta(seconds=2))

    def test_resolving_requires_diagnosis_and_resolution(self):
        ticket = self.make_ticket()
        with self.assertRaises(ValidationError):
            ticket.transition_to(Ticket.Status.RESOLVED, self.agent)
        self.assertEqual(TicketActivity.objects.count(), 0)

    def test_transition_records_activity_and_resolution_time(self):
        ticket = self.make_ticket(diagnosis="DNS mal configurado", resolution="Se renovó DNS")
        changed = ticket.transition_to(Ticket.Status.RESOLVED, self.agent, "Validado con usuario")
        self.assertTrue(changed)
        self.assertIsNotNone(ticket.resolved_at)
        self.assertIsNotNone(ticket.resolution_time)
        activity = ticket.activities.get()
        self.assertEqual(activity.activity_type, TicketActivity.ActivityType.STATUS_CHANGE)
        self.assertEqual(activity.old_value, Ticket.Status.OPEN)
        self.assertEqual(activity.new_value, Ticket.Status.RESOLVED)

    def test_reopening_recalculates_sla(self):
        ticket = self.make_ticket(diagnosis="Diagnóstico", resolution="Solución")
        ticket.transition_to(Ticket.Status.RESOLVED, self.agent)
        old_due_at = ticket.due_at
        ticket.transition_to(Ticket.Status.IN_PROGRESS, self.agent)
        self.assertIsNone(ticket.resolved_at)
        self.assertGreater(ticket.due_at, old_due_at)

    def test_visibility_is_limited_for_regular_users(self):
        own = self.make_ticket()
        self.make_ticket(title="Ajeno", requester=self.other_user)
        self.assertEqual(list(Ticket.objects.visible_to(self.requester)), [own])
        self.assertEqual(Ticket.objects.visible_to(self.agent).count(), 2)

    def test_create_form_limits_regular_user_assets(self):
        other_asset = Asset.objects.create(
            asset_tag="PC-002", name="PC ajena", assigned_to=self.other_user
        )
        form = TicketCreateForm(user=self.requester)
        self.assertIn(self.asset, form.fields["asset"].queryset)
        self.assertNotIn(other_asset, form.fields["asset"].queryset)

    def test_status_form_validates_resolution_fields(self):
        form = TicketStatusForm(
            {"status": Ticket.Status.RESOLVED, "diagnosis": "", "resolution": ""}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("diagnosis", form.errors)
        self.assertIn("resolution", form.errors)
