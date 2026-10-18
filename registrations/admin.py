from django.contrib import admin

from .models import Registration, UserProfile


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "registered_at")
    list_filter = ("event", "registered_at")
    search_fields = ("event__title", "user__username", "user__email")


admin.site.register(UserProfile)
