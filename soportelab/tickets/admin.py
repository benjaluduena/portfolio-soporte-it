from django.contrib import admin

from .models import Category, Ticket, TicketActivity


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


class TicketActivityInline(admin.TabularInline):
    model = TicketActivity
    extra = 0
    readonly_fields = ("author", "activity_type", "message", "old_value", "new_value", "created_at")
    can_delete = False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "status", "priority", "requester", "assignee", "due_at")
    list_filter = ("status", "priority", "ticket_type", "category")
    search_fields = ("code", "title", "description", "requester__username", "assignee__username")
    list_select_related = ("category", "requester", "assignee", "asset")
    readonly_fields = ("code", "created_at", "updated_at", "due_at", "resolved_at", "closed_at")
    inlines = (TicketActivityInline,)


@admin.register(TicketActivity)
class TicketActivityAdmin(admin.ModelAdmin):
    list_display = ("ticket", "activity_type", "author", "created_at")
    list_filter = ("activity_type",)
    search_fields = ("ticket__code", "message", "author__username")
    list_select_related = ("ticket", "author")
    readonly_fields = ("created_at",)
