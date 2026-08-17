from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import RegisterForm
from .models import EmailOTP, User
from .utils import (
    create_and_send_otp,
    get_resend_wait_seconds,
    has_exceeded_hourly_limit,
)


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        existing_unverified = User.objects.filter(
            email=email, is_email_verified=False
        ).first()

        if existing_unverified:
            request.session["pending_user_id"] = existing_unverified.id

            if has_exceeded_hourly_limit(existing_unverified, "verify_email"):
                return render(
                    request,
                    "accounts/verify_email.html",
                    {
                        "error": "Too many code requests. Please try again after an hour."
                    },
                )

            wait = get_resend_wait_seconds(existing_unverified, "verify_email")
            if wait > 0:
                return render(
                    request,
                    "accounts/verify_email.html",
                    {
                        "error": f"A code was already sent. Please wait {wait} seconds before trying again."
                    },
                )

            create_and_send_otp(existing_unverified, "verify_email")
            return redirect("accounts:verify_email")

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_and_send_otp(user, "verify_email")
            request.session["pending_user_id"] = user.id
            return redirect("accounts:verify_email")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def verify_email_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("accounts:register")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        entered_code = request.POST.get("code", "").strip()

        matched_otp = (
            EmailOTP.objects.filter(
                user=user, purpose="verify_email", code=entered_code
            )
            .order_by("-created_at")
            .first()
        )

        if not matched_otp:
            return render(
                request,
                "accounts/verify_email.html",
                {"error": "Incorrect code. Please check your email and try again."},
            )

        if matched_otp.is_used:
            return render(
                request,
                "accounts/verify_email.html",
                {
                    "error": "This code has already been used. Please request a new one below."
                },
            )

        if matched_otp.is_expired():
            return render(
                request,
                "accounts/verify_email.html",
                {"error": "This code has expired. Please request a new one below."},
            )

        matched_otp.is_used = True
        matched_otp.save()
        user.is_email_verified = True
        user.save()

        login(request, user)
        del request.session["pending_user_id"]
        return redirect("accounts:profile")

    return render(request, "accounts/verify_email.html")


def resend_otp_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("accounts:register")

    user = User.objects.get(id=user_id)

    if has_exceeded_hourly_limit(user, "verify_email"):
        return render(
            request,
            "accounts/verify_email.html",
            {"error": "Too many code requests. Please try again after an hour."},
        )

    wait = get_resend_wait_seconds(user, "verify_email")
    if wait > 0:
        return render(
            request,
            "accounts/verify_email.html",
            {"error": f"Please wait {wait} seconds before requesting a new code."},
        )

    create_and_send_otp(user, "verify_email")
    return render(
        request, "accounts/verify_email.html", {"info": "A new code has been sent."}
    )


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


class CustomLogoutView(LogoutView):
    next_page = "accounts:login"


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user": request.user})
