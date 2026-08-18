from django import forms

from tickets.forms import FormControlMixin

from .models import Asset


class AssetForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Asset
        fields = (
            "asset_tag",
            "name",
            "asset_type",
            "brand",
            "model",
            "serial_number",
            "status",
            "assigned_to",
            "location",
            "operating_system",
            "notes",
        )
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_form_classes()
