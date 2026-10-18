from rest_framework import serializers

from .models import Category, Event
from registrations.models import Registration


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    attendee_count = serializers.IntegerField(source="registration_total", read_only=True)
    seats_remaining = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id", "title", "category", "starts_at", "location", "map_url", "description",
            "capacity", "attendee_count", "seats_remaining", "is_full", "is_cancelled", "image_url",
        )

    def get_seats_remaining(self, obj):
        return max(obj.capacity - getattr(obj, "registration_total", obj.registrations.count()), 0)

    def get_is_full(self, obj):
        return self.get_seats_remaining(obj) == 0

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ("id", "event", "registered_at")
        read_only_fields = fields
