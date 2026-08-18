from django.contrib import admin

from .models import KnowledgeArticle


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "author", "updated_at")
    list_filter = ("status", "category")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_tickets",)
    readonly_fields = ("created_at", "updated_at")
