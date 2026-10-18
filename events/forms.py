from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("title", "category", "starts_at", "location", "map_url", "description", "capacity", "image")
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity < 1:
            raise forms.ValidationError("Capacity must be at least one seat.")
        if self.instance.pk and capacity < self.instance.registrations.count():
            raise forms.ValidationError("Capacity cannot be lower than the current registration count.")
        return capacity
