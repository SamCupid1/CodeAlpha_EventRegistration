import csv

from django.contrib import admin
from django.http import HttpResponse

from registrations.models import Registration

from .models import Category, Event


@admin.action(description="Export selected event registrations as CSV")
def export_registrations(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="event-registrations.csv"'
    writer = csv.writer(response)
    writer.writerow(("Event", "Username", "Email", "Registered at"))
    for registration in Registration.objects.filter(event__in=queryset).select_related("event", "user"):
        writer.writerow((registration.event.title, registration.user.username, registration.user.email, registration.registered_at.isoformat()))
    return response


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "starts_at", "location", "capacity", "is_cancelled")
    list_filter = ("category", "is_cancelled", "starts_at")
    search_fields = ("title", "location")
    actions = (export_registrations,)


admin.site.register(Category)
