from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=180)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="events")
    starts_at = models.DateTimeField(db_index=True)
    location = models.CharField(max_length=200)
    map_url = models.URLField(blank=True)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    image = models.ImageField(upload_to="events/", blank=True)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("starts_at",)
        indexes = [models.Index(fields=("category", "starts_at"), name="event_cat_date_idx")]

    def __str__(self):
        return self.title

    @property
    def attendee_count(self):
        return self.registrations.count()

    @property
    def seats_remaining(self):
        return max(self.capacity - self.attendee_count, 0)

    @property
    def is_full(self):
        return self.seats_remaining == 0

    @property
    def is_past(self):
        return self.starts_at < timezone.now()
