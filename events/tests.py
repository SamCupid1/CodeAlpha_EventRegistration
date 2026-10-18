from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Category, Event
from registrations.models import Registration


class EventPlatformTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Technology", slug="technology")
        self.event = Event.objects.create(
            title="Build Night",
            category=self.category,
            starts_at=timezone.now() + timedelta(days=10),
            location="Foundry Hall",
            description="A community event.",
            capacity=1,
        )

    def test_signup_sends_single_account_notification_without_verification_flow(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "casey",
                "email": "casey@example.com",
                "password1": "StrongPass!123",
                "password2": "StrongPass!123",
            },
        )

        self.assertRedirects(response, reverse("event_list"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("account has been created at EventCreate", mail.outbox[0].body)
        self.assertNotIn("verify", mail.outbox[0].body.lower())
        self.assertTrue(hasattr(User.objects.get(username="casey"), "profile"))

    def test_event_registration_reserves_capacity_and_blocks_duplicate(self):
        user = User.objects.create_user(username="alex", password="StrongPass!123")
        self.client.force_login(user)

        first = self.client.post(reverse("register_event", args=(self.event.pk,)))
        second = self.client.post(reverse("register_event", args=(self.event.pk,)))

        self.assertRedirects(first, reverse("event_detail", args=(self.event.pk,)))
        self.assertRedirects(second, reverse("event_detail", args=(self.event.pk,)))
        self.assertEqual(Registration.objects.filter(event=self.event).count(), 1)
        self.assertEqual(self.event.seats_remaining, 0)

    def test_cancelled_registration_releases_the_seat(self):
        user = User.objects.create_user(username="jules", password="StrongPass!123")
        registration = Registration.objects.create(user=user, event=self.event)
        self.client.force_login(user)

        response = self.client.post(reverse("cancel_registration", args=(self.event.pk,)))

        self.assertRedirects(response, reverse("profile"))
        self.assertFalse(Registration.objects.filter(pk=registration.pk).exists())
        self.assertEqual(self.event.seats_remaining, 1)

    def test_event_list_filters_by_category_and_location(self):
        response = self.client.get(reverse("event_list"), {"category": "technology", "location": "foundry"})

        self.assertContains(response, "Build Night")
        self.assertNotContains(response, "No events match")


class EventAPITests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name="Community", slug="community")
        self.event = Event.objects.create(
            title="Neighborhood Forum",
            category=category,
            starts_at=timezone.now() + timedelta(days=4),
            location="Town Hall",
            description="Talk and listen.",
            capacity=2,
        )

    def test_public_event_api_returns_seat_count(self):
        response = self.client.get(reverse("api_event_detail", args=(self.event.pk,)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["seats_remaining"], 2)
        self.assertEqual(response.data["attendee_count"], 0)

    def test_registration_api_requires_authentication_and_registers_user(self):
        unauthenticated = self.client.post(reverse("api_event_register", args=(self.event.pk,)))
        self.assertEqual(unauthenticated.status_code, 403)

        user = User.objects.create_user(username="sam", password="StrongPass!123")
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse("api_event_register", args=(self.event.pk,)))

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Registration.objects.filter(user=user, event=self.event).exists())
