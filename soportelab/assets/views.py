from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import StaffRequiredMixin

from .forms import AssetForm
from .models import Asset


class VisibleAssetMixin:
    def get_queryset(self):
        queryset = Asset.objects.select_related("assigned_to")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(assigned_to=self.request.user)


class AssetListView(LoginRequiredMixin, VisibleAssetMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(asset_tag__icontains=query)
                | Q(name__icontains=query)
                | Q(serial_number__icontains=query)
                | Q(assigned_to__username__icontains=query)
            )
        for field, parameter in (("asset_type", "type"), ("status", "status")):
            value = self.request.GET.get(parameter)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type_choices"] = Asset.AssetType.choices
        context["status_choices"] = Asset.Status.choices
        return context


class AssetDetailView(LoginRequiredMixin, VisibleAssetMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"
    slug_field = "asset_tag"
    slug_url_kwarg = "asset_tag"
    def get_queryset(self):
        return super().get_queryset().prefetch_related("tickets")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_tickets"] = self.object.tickets.select_related("category", "requester")
        return context


class AssetCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Activo creado.")
        return super().form_valid(form)


class AssetUpdateView(LoginRequiredMixin, StaffRequiredMixin, VisibleAssetMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    slug_field = "asset_tag"
    slug_url_kwarg = "asset_tag"
    def form_valid(self, form):
        messages.success(self.request, "Activo actualizado.")
        return super().form_valid(form)
