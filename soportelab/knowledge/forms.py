from django import forms

from tickets.forms import FormControlMixin

from .models import KnowledgeArticle


class KnowledgeArticleForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = KnowledgeArticle
        fields = ("title", "slug", "category", "summary", "content", "status", "related_tickets")
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 12}),
            "related_tickets": forms.SelectMultiple(attrs={"size": 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_form_classes()
