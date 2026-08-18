from django.contrib import admin

from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("asset_tag", "name", "asset_type", "status", "assigned_to", "location")
    list_filter = ("asset_type", "status", "location")
    search_fields = ("asset_tag", "name", "serial_number", "assigned_to__username")
    list_select_related = ("assigned_to",)
    readonly_fields = ("created_at", "updated_at")
