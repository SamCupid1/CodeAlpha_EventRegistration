from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Category, Event


class Command(BaseCommand):
    help = "Load demo event categories and upcoming events."

    def handle(self, *args, **options):
        category_names = ("Technology", "Community", "Design", "Food & Culture")
        categories = {
            name: Category.objects.get_or_create(name=name, defaults={"slug": name.lower().replace(" & ", "-").replace(" ", "-")})[0]
            for name in category_names
        }
        samples = (
            ("Build Night: Ideas to Impact", "Technology", "Harbor Innovation Studio", "A friendly evening of short talks, collaborative demos, and practical conversations for people building useful things.", 80, 7),
            ("City Makers Weekend", "Community", "Foundry Hall", "Meet local makers, browse hands-on workshops, and share the projects shaping our neighborhood.", 120, 15),
            ("Designing for Everyday Life", "Design", "Northline Gallery", "A thoughtful conversation about inclusive products, clear interfaces, and the small details that make experiences work.", 55, 24),
            ("A Table Across Cultures", "Food & Culture", "Market House", "An informal community dinner celebrating the stories and recipes that bring people together.", 40, 31),
        )
        for title, category, location, description, capacity, days in samples:
            Event.objects.get_or_create(
                title=title,
                defaults={
                    "category": categories[category],
                    "starts_at": timezone.now() + timedelta(days=days),
                    "location": location,
                    "description": description,
                    "capacity": capacity,
                    "map_url": "",
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(samples)} sample events."))
