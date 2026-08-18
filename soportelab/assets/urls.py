from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("", views.AssetListView.as_view(), name="list"),
    path("nuevo/", views.AssetCreateView.as_view(), name="create"),
    path("<int:pk>/", views.AssetDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.AssetUpdateView.as_view(), name="update"),
    path("<int:pk>/editar/", views.AssetUpdateView.as_view(), name="edit"),
    path("codigo/<str:asset_tag>/", views.AssetDetailView.as_view(), name="detail_by_code"),
]
