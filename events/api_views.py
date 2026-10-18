from django.db.models import Count
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from registrations.models import Registration
from .serializers import EventSerializer, RegistrationSerializer


class EventListAPI(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = Event.objects.select_related("category").annotate(registration_total=Count("registrations"))
        category = self.request.query_params.get("category")
        location = self.request.query_params.get("location")
        start = self.request.query_params.get("from")
        end = self.request.query_params.get("to")
        search = self.request.query_params.get("q")
        try:
            parsed_start = parse_date(start) if start else None
            parsed_end = parse_date(end) if end else None
        except ValueError as exc:
            raise ValidationError({"date": "Use YYYY-MM-DD for date filters."}) from exc
        if (start and parsed_start is None) or (end and parsed_end is None):
            raise ValidationError({"date": "Use YYYY-MM-DD for date filters."})
        if category:
            queryset = queryset.filter(category__slug=category)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if parsed_start:
            queryset = queryset.filter(starts_at__date__gte=parsed_start)
        if parsed_end:
            queryset = queryset.filter(starts_at__date__lte=parsed_end)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset


class EventDetailAPI(generics.RetrieveAPIView):
    queryset = Event.objects.select_related("category").annotate(registration_total=Count("registrations"))
    serializer_class = EventSerializer
    permission_classes = (permissions.AllowAny,)


class EventRegistrationAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            with transaction.atomic():
                event = Event.objects.select_for_update().get(pk=pk)
                if event.is_cancelled or event.starts_at <= timezone.now():
                    raise ValidationError({"detail": "Registration is not available for this event."})
                if event.registrations.count() >= event.capacity:
                    raise ValidationError({"detail": "This event is full."})
                registration = Registration.objects.create(user=request.user, event=event)
        except Event.DoesNotExist as exc:
            raise NotFound("Event not found.") from exc
        except IntegrityError as exc:
            raise ValidationError({"detail": "You are already registered for this event."}) from exc
        return Response(RegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)
