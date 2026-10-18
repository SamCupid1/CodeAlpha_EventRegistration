import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mass_mail
from django.db import IntegrityError, transaction
from django.db.models import Count, F, IntegerField, Q
from django.db.models.functions import Greatest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EventForm
from .models import Category, Event
from registrations.models import Registration


def event_list(request):
    events = Event.objects.select_related("category").annotate(
        registration_total=Count("registrations"),
        remaining_seat_count=Greatest(F("capacity") - Count("registrations"), 0, output_field=IntegerField()),
    )
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    location = request.GET.get("location", "").strip()
    start_date = request.GET.get("from", "").strip()
    end_date = request.GET.get("to", "").strip()

    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        events = events.filter(category__slug=category)
    if location:
        events = events.filter(location__icontains=location)
    try:
        parsed_start = parse_date(start_date) if start_date else None
        parsed_end = parse_date(end_date) if end_date else None
    except ValueError:
        parsed_start = parsed_end = None
    if (start_date and parsed_start is None) or (end_date and parsed_end is None):
        messages.error(request, "Enter dates in YYYY-MM-DD format.")
    if parsed_start:
        events = events.filter(starts_at__date__gte=parsed_start)
    if parsed_end:
        events = events.filter(starts_at__date__lte=parsed_end)

    return render(
        request,
        "events/event_list.html",
        {
            "events": events,
            "categories": Category.objects.all(),
            "filters": {"q": query, "category": category, "location": location, "from": start_date, "to": end_date},
        },
    )


def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related("category").annotate(registration_total=Count("registrations")), pk=pk)
    is_registered = request.user.is_authenticated and event.registrations.filter(user=request.user).exists()
    return render(request, "events/event_detail.html", {"event": event, "is_registered": is_registered})


@login_required
@require_POST
def register_event(request, pk):
    try:
        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=pk)
            if event.is_cancelled or event.starts_at <= timezone.now():
                messages.error(request, "Registration is not available for this event.")
            elif event.registrations.count() >= event.capacity:
                messages.error(request, "This event is full.")
            else:
                Registration.objects.create(user=request.user, event=event)
                messages.success(request, "You are registered for this event.")
    except IntegrityError:
        messages.info(request, "You are already registered for this event.")
    return redirect("event_detail", pk=pk)


@login_required
@require_POST
def cancel_registration(request, pk):
    registration = get_object_or_404(Registration, event_id=pk, user=request.user)
    registration.delete()
    messages.success(request, "Your registration was cancelled and the seat is available again.")
    return redirect("profile")


@login_required
def profile(request):
    registrations = Registration.objects.filter(user=request.user).select_related("event", "event__category")
    now = timezone.now()
    return render(
        request,
        "events/profile.html",
        {
            "upcoming": registrations.filter(event__starts_at__gte=now, event__is_cancelled=False),
            "past": registrations.filter(Q(event__starts_at__lt=now) | Q(event__is_cancelled=True)),
        },
    )


@staff_member_required
def staff_dashboard(request):
    events = Event.objects.select_related("category").annotate(registration_total=Count("registrations")).order_by("starts_at")
    near_capacity = [event for event in events if event.capacity and event.registration_total / event.capacity >= 0.8]
    return render(
        request,
        "events/staff_dashboard.html",
        {
            "events": events,
            "total_events": Event.objects.count(),
            "total_registrations": Registration.objects.count(),
            "near_capacity": near_capacity,
        },
    )


@staff_member_required
def event_create(request):
    form = EventForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        event = form.save()
        messages.success(request, "Event created.")
        return redirect("event_detail", pk=event.pk)
    return render(request, "events/event_form.html", {"form": form, "heading": "Create an event"})


@staff_member_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, request.FILES or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("event_detail", pk=event.pk)
    return render(request, "events/event_form.html", {"form": form, "heading": "Edit event", "event": event})


@staff_member_required
@require_POST
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, "Event deleted.")
    return redirect("staff_dashboard")


@staff_member_required
@require_POST
def event_cancel(request, pk):
    with transaction.atomic():
        event = get_object_or_404(Event.objects.select_for_update(), pk=pk)
        event.is_cancelled = True
        event.save(update_fields=("is_cancelled",))
        recipients = list(
            Registration.objects.filter(event=event).select_related("user").values_list("user__email", "user__username")
        )
    messages_to_send = [
        (
            f"Event cancelled: {event.title}",
            f"Hello {username}, the event {event.title} scheduled for {timezone.localtime(event.starts_at):%B %d, %Y} has been cancelled.",
            None,
            [email],
        )
        for email, username in recipients
        if email
    ]
    if messages_to_send:
        send_mass_mail(tuple(messages_to_send), fail_silently=False)
    messages.success(request, "The event has been cancelled and registered attendees have been notified.")
    return redirect("staff_dashboard")


@staff_member_required
def event_registrations_csv(request, pk):
    event = get_object_or_404(Event, pk=pk)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="event-{event.pk}-registrations.csv"'
    writer = csv.writer(response)
    writer.writerow(("Event", "Username", "Email", "Registered at"))
    for registration in event.registrations.select_related("user"):
        writer.writerow((event.title, registration.user.username, registration.user.email, registration.registered_at.isoformat()))
    return response
