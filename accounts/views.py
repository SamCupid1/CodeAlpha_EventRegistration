from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import SignUpForm


def signup(request):
    if request.user.is_authenticated:
        return redirect("event_list")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        send_mail(
            subject="Your EventCreate account is ready",
            message=(
                f"Hello {user.username}, your account has been created at EventCreate. "
                "You can now sign in and start using the platform. "
                "If you did not create this account, please contact support."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        login(request, user)
        messages.success(request, "Your account is ready. Welcome to EventCreate.")
        return redirect(request.GET.get("next") or reverse("event_list"))

    return render(request, "accounts/signup.html", {"form": form})
