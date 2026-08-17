from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailOTP

RESEND_COOLDOWN_SECONDS = 30
MAX_OTP_PER_HOUR = 5


def get_resend_wait_seconds(user, purpose):
    last_otp = (
        EmailOTP.objects.filter(user=user, purpose=purpose)
        .order_by("-created_at")
        .first()
    )
    if not last_otp:
        return 0
    elapsed = (timezone.now() - last_otp.created_at).total_seconds()
    remaining = RESEND_COOLDOWN_SECONDS - elapsed
    return max(0, int(remaining))


def has_exceeded_hourly_limit(user, purpose):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    count = EmailOTP.objects.filter(
        user=user, purpose=purpose, created_at__gte=one_hour_ago
    ).count()
    return count >= MAX_OTP_PER_HOUR


def create_and_send_otp(user, purpose):
    EmailOTP.objects.filter(user=user, purpose=purpose, is_used=False).update(
        is_invalidated=True
    )

    code = EmailOTP.generate_code()
    EmailOTP.objects.create(user=user, code=code, purpose=purpose)

    if purpose == "verify_email":
        subject = "Panchakanya Collections - Verify Your Email"
        message = (
            f"Hi {user.username},\n\n"
            f"Use this code to verify your email address:\n\n"
            f"{code}\n\n"
            f"This code is for EMAIL VERIFICATION and expires in 5 minutes.\n"
            f"If you did not request this, please ignore this email."
        )
    else:
        subject = "Panchakanya Collections - Password Reset Code"
        message = (
            f"Hi {user.username},\n\n"
            f"Use this code to reset your password:\n\n"
            f"{code}\n\n"
            f"This code is for PASSWORD RESET and expires in 5 minutes.\n"
            f"If you did not request this, please ignore this email."
        )

    send_mail(subject, message, None, [user.email])
