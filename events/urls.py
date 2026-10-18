from django.urls import path

from . import views

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/register/", views.register_event, name="register_event"),
    path("events/<int:pk>/cancel-registration/", views.cancel_registration, name="cancel_registration"),
    path("profile/", views.profile, name="profile"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/events/new/", views.event_create, name="event_create"),
    path("staff/events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("staff/events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("staff/events/<int:pk>/cancel/", views.event_cancel, name="event_cancel"),
    path("staff/events/<int:pk>/registrations.csv", views.event_registrations_csv, name="event_registrations_csv"),
]
