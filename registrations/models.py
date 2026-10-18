from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} profile"


class Registration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_registrations")
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-registered_at",)
        constraints = [
            models.UniqueConstraint(fields=("user", "event"), name="unique_user_event_registration"),
        ]
        indexes = [models.Index(fields=("event", "registered_at"), name="registration_event_date_idx")]

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
