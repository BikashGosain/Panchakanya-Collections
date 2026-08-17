from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import ProfileEditForm, RegisterForm
from .models import EmailOTP, User
from .utils import (
    create_and_send_otp,
    get_resend_wait_seconds,
    has_exceeded_hourly_limit,
)


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        existing_unverified = User.objects.filter(
            email=email,
            is_email_verified=False,
        ).first()

        # Existing unverified registration
        if existing_unverified:
            form = RegisterForm(
                request.POST,
                instance=existing_unverified,
            )

            if not form.is_valid():
                return render(
                    request,
                    "accounts/register.html",
                    {"form": form},
                )

            user = form.save()

            user.is_active = False
            user.is_email_verified = False
            user.save(
                update_fields=[
                    "is_active",
                    "is_email_verified",
                ]
            )

            request.session["pending_user_id"] = user.id

            if has_exceeded_hourly_limit(
                user,
                "verify_email",
            ):
                return render(
                    request,
                    "accounts/register.html",
                    {
                        "form": form,
                        "error": (
                            "Too many code requests. Please try again after an hour."
                        ),
                    },
                )

            wait = get_resend_wait_seconds(
                user,
                "verify_email",
            )

            if wait > 0:
                return render(
                    request,
                    "accounts/register.html",
                    {
                        "form": form,
                        "error": (
                            f"A code was already sent. "
                            f"Please wait {wait} seconds "
                            f"before requesting another code."
                        ),
                    },
                )

            create_and_send_otp(
                user,
                "verify_email",
            )

            return redirect("accounts:verify_email")

        # New registration
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            user.is_active = False
            user.is_email_verified = False
            user.save(
                update_fields=[
                    "is_active",
                    "is_email_verified",
                ]
            )

            create_and_send_otp(
                user,
                "verify_email",
            )

            request.session["pending_user_id"] = user.id

            return redirect("accounts:verify_email")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


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

        if matched_otp.is_invalidated:
            return render(
                request,
                "accounts/verify_email.html",
                {
                    "error": "This code is no longer valid because a newer code was requested."
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
        user.is_active = True
        user.save(update_fields=["is_email_verified", "is_active"])

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        request.session.pop("pending_user_id", None)
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


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        user = User.objects.filter(email=email).first()

        if user:
            if has_exceeded_hourly_limit(user, "reset_password"):
                return render(
                    request,
                    "accounts/forgot_password.html",
                    {
                        "error": "Too many reset requests. Please try again after an hour."
                    },
                )
            wait = get_resend_wait_seconds(user, "reset_password")
            if wait > 0:
                return render(
                    request,
                    "accounts/forgot_password.html",
                    {"error": f"Please wait {wait} seconds before requesting again."},
                )
            create_and_send_otp(user, "reset_password")
            request.session["reset_user_id"] = user.id
            return redirect("accounts:reset_password")

        return render(
            request,
            "accounts/forgot_password.html",
            {"error": "No account found with that email."},
        )

    return render(request, "accounts/forgot_password.html")


def reset_password_view(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("accounts:forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        entered_code = request.POST.get("code", "").strip()

        matched_otp = (
            EmailOTP.objects.filter(
                user=user, purpose="reset_password", code=entered_code
            )
            .order_by("-created_at")
            .first()
        )

        if not matched_otp:
            return render(
                request,
                "accounts/reset_password.html",
                {"error": "Incorrect code. Please check your email and try again."},
            )
        if matched_otp.is_used:
            return render(
                request,
                "accounts/reset_password.html",
                {"error": "This code has already been used. Please request a new one."},
            )
        if matched_otp.is_invalidated:
            return render(
                request,
                "accounts/reset_password.html",
                {
                    "error": "This code is no longer valid because a newer code was requested."
                },
            )
        if matched_otp.is_expired():
            return render(
                request,
                "accounts/reset_password.html",
                {"error": "This code has expired. Please request a new one."},
            )

        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            matched_otp.is_used = True
            matched_otp.save()
            del request.session["reset_user_id"]
            return redirect("accounts:login")

        return render(
            request, "accounts/reset_password.html", {"error": form.errors.as_text()}
        )

    return render(request, "accounts/reset_password.html")


def resend_reset_otp_view(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("accounts:forgot_password")

    user = User.objects.get(id=user_id)

    if has_exceeded_hourly_limit(user, "reset_password"):
        return render(
            request,
            "accounts/reset_password.html",
            {"error": "Too many code requests. Please try again after an hour."},
        )

    wait = get_resend_wait_seconds(user, "reset_password")
    if wait > 0:
        return render(
            request,
            "accounts/reset_password.html",
            {"error": f"Please wait {wait} seconds before requesting a new code."},
        )

    create_and_send_otp(user, "reset_password")
    return render(
        request, "accounts/reset_password.html", {"info": "A new code has been sent."}
    )


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user": request.user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "accounts/edit_profile.html", {"form": form})
