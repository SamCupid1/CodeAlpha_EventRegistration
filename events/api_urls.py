from django.urls import path

from .api_views import EventDetailAPI, EventListAPI, EventRegistrationAPI

urlpatterns = [
    path("events/", EventListAPI.as_view(), name="api_event_list"),
    path("events/<int:pk>/", EventDetailAPI.as_view(), name="api_event_detail"),
    path("events/<int:pk>/register/", EventRegistrationAPI.as_view(), name="api_event_register"),
]
