from django.urls import path

from . import views

app_name = "knowledge"

urlpatterns = [
    path("", views.KnowledgeArticleListView.as_view(), name="list"),
    path("nuevo/", views.KnowledgeArticleCreateView.as_view(), name="create"),
    path("<int:pk>/", views.KnowledgeArticleDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.KnowledgeArticleUpdateView.as_view(), name="update"),
    path("<int:pk>/editar/", views.KnowledgeArticleUpdateView.as_view(), name="edit"),
    path("articulo/<slug:slug>/", views.KnowledgeArticleDetailView.as_view(), name="detail_by_slug"),
]
