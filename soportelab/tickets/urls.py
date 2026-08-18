from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.TicketListView.as_view(), name="list"),
    path("nuevo/", views.TicketCreateView.as_view(), name="create"),
    path("<int:pk>/", views.TicketDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.TicketUpdateView.as_view(), name="update"),
    path("<int:pk>/editar/", views.TicketUpdateView.as_view(), name="edit"),
    path("<int:pk>/estado/", views.TicketStatusView.as_view(), name="status"),
    path("<int:pk>/comentar/", views.TicketCommentView.as_view(), name="add_comment"),
    path("<int:pk>/comentar/", views.TicketCommentView.as_view(), name="comment"),
    path("<int:pk>/resolver/", views.TicketResolveView.as_view(), name="resolve"),
    path("codigo/<str:code>/", views.TicketDetailView.as_view(), name="detail_by_code"),
]
