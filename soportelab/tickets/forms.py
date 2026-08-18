from django import forms
from django.contrib.auth import get_user_model

from assets.models import Asset

from .models import Category, Ticket


class FormControlMixin:
    def _apply_form_classes(self):
        for field in self.fields.values():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = f"{field.widget.attrs.get('class', '')} {css_class}".strip()


class TicketCreateForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "description", "ticket_type", "category", "priority", "asset")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["category"].queryset = Category.objects.filter(is_active=True)
        if user and not user.is_staff:
            self.fields["asset"].queryset = Asset.objects.filter(assigned_to=user)
        self._apply_form_classes()


class TicketUpdateForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = (
            "title",
            "description",
            "ticket_type",
            "category",
            "priority",
            "requester",
            "assignee",
            "asset",
            "diagnosis",
            "root_cause",
            "resolution",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "diagnosis": forms.Textarea(attrs={"rows": 3}),
            "root_cause": forms.Textarea(attrs={"rows": 3}),
            "resolution": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(is_active=True)
        self.fields["assignee"].queryset = get_user_model().objects.filter(is_staff=True, is_active=True)
        self._apply_form_classes()


class TicketStatusForm(FormControlMixin, forms.Form):
    status = forms.ChoiceField(label="Nuevo estado", choices=Ticket.Status.choices)
    diagnosis = forms.CharField(label="Diagnóstico", required=False, widget=forms.Textarea(attrs={"rows": 3}))
    root_cause = forms.CharField(label="Causa raíz", required=False, widget=forms.Textarea(attrs={"rows": 3}))
    resolution = forms.CharField(label="Resolución", required=False, widget=forms.Textarea(attrs={"rows": 3}))
    message = forms.CharField(label="Nota del cambio", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, ticket=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticket = ticket
        if ticket:
            for name in ("diagnosis", "root_cause", "resolution"):
                self.fields[name].initial = getattr(ticket, name)
        self._apply_form_classes()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("status") in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
            if not cleaned.get("diagnosis", "").strip():
                self.add_error("diagnosis", "Es obligatorio para resolver el ticket.")
            if not cleaned.get("resolution", "").strip():
                self.add_error("resolution", "Es obligatoria para resolver el ticket.")
        return cleaned


class TicketCommentForm(FormControlMixin, forms.Form):
    message = forms.CharField(label="Comentario", widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_form_classes()
