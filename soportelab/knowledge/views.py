from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import StaffRequiredMixin

from .forms import KnowledgeArticleForm
from .models import KnowledgeArticle
from tickets.models import Category


class ArticleQuerysetMixin:
    def get_queryset(self):
        return KnowledgeArticle.objects.visible_to(self.request.user).select_related("category", "author")


class KnowledgeArticleListView(ArticleQuerysetMixin, ListView):
    model = KnowledgeArticle
    template_name = "knowledge/article_list.html"
    context_object_name = "articles"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query)
            )
        category = self.request.GET.get("category")
        if category and category.isdigit():
            queryset = queryset.filter(category_id=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visible = KnowledgeArticle.objects.visible_to(self.request.user)
        context["article_count"] = visible.count()
        context["categories"] = Category.objects.filter(
            knowledge_articles__in=visible
        ).annotate(article_count=Count("knowledge_articles", distinct=True)).distinct()
        return context


class KnowledgeArticleDetailView(ArticleQuerysetMixin, DetailView):
    model = KnowledgeArticle
    template_name = "knowledge/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class KnowledgeArticleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = KnowledgeArticle
    form_class = KnowledgeArticleForm
    template_name = "knowledge/article_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Artículo creado.")
        return super().form_valid(form)


class KnowledgeArticleUpdateView(
    LoginRequiredMixin, StaffRequiredMixin, ArticleQuerysetMixin, UpdateView
):
    model = KnowledgeArticle
    form_class = KnowledgeArticleForm
    template_name = "knowledge/article_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    def form_valid(self, form):
        messages.success(self.request, "Artículo actualizado.")
        return super().form_valid(form)
