# Create your tests here.
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import EmailOTP, User


class RegistrationAndVerificationTests(TestCase):
    def setUp(self):
        self.register_data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "phone_number": "9812345678",
            "address": "Test Address",
            "city": "Kathmandu",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        }

    def test_register_sends_otp_and_creates_unverified_user(self):
        response = self.client.post(reverse("accounts:register"), self.register_data)
        user = User.objects.get(email="testuser@example.com")

        self.assertFalse(user.is_email_verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertRedirects(response, reverse("accounts:verify_email"))

    def test_verify_with_correct_code_activates_user(self):
        self.client.post(reverse("accounts:register"), self.register_data)
        user = User.objects.get(email="testuser@example.com")
        otp = EmailOTP.objects.filter(user=user, purpose="verify_email").latest(
            "created_at"
        )

        response = self.client.post(
            reverse("accounts:verify_email"), {"code": otp.code}
        )

        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        self.assertRedirects(response, reverse("dashboard:profile"))

    def test_verify_with_wrong_code_shows_error(self):
        self.client.post(reverse("accounts:register"), self.register_data)
        response = self.client.post(
            reverse("accounts:verify_email"), {"code": "000000"}
        )

        self.assertContains(response, "Incorrect code")

    def test_verify_with_used_code_shows_error(self):
        self.client.post(reverse("accounts:register"), self.register_data)
        user = User.objects.get(email="testuser@example.com")
        otp = EmailOTP.objects.filter(user=user, purpose="verify_email").latest(
            "created_at"
        )

        self.client.post(reverse("accounts:verify_email"), {"code": otp.code})

        session = self.client.session
        session["pending_user_id"] = user.id
        session.save()

        response = self.client.post(
            reverse("accounts:verify_email"), {"code": otp.code}
        )
        self.assertContains(response, "already been used")

    def test_resend_invalidates_old_code(self):
        from apps.accounts.utils import create_and_send_otp

        self.client.post(reverse("accounts:register"), self.register_data)
        user = User.objects.get(email="testuser@example.com")
        old_otp = EmailOTP.objects.filter(user=user, purpose="verify_email").latest(
            "created_at"
        )

        create_and_send_otp(user, "verify_email")

        response = self.client.post(
            reverse("accounts:verify_email"), {"code": old_otp.code}
        )
        self.assertContains(response, "no longer valid")


from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class PasswordResetTests(TestCase):
    def setUp(self):
        site = Site.objects.get_current()
        app = SocialApp.objects.create(
            provider="google",
            name="Test Google App",
            client_id="test-client-id",
            secret="test-secret",
        )
        app.sites.add(site)

        self.user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="OldPass1!",
            phone_number="9811111111",
            address="Some Address",
            city="Kathmandu",
            is_email_verified=True,
        )

    def test_forgot_password_sends_otp(self):
        response = self.client.post(
            reverse("accounts:forgot_password"), {"email": "resetuser@example.com"}
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertRedirects(response, reverse("accounts:reset_password"))

    def test_reset_password_with_correct_code_changes_password(self):
        self.client.post(
            reverse("accounts:forgot_password"), {"email": "resetuser@example.com"}
        )
        otp = EmailOTP.objects.filter(user=self.user, purpose="reset_password").latest(
            "created_at"
        )

        response = self.client.post(
            reverse("accounts:reset_password"),
            {
                "code": otp.code,
                "new_password1": "NewStrongPass1!",
                "new_password2": "NewStrongPass1!",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass1!"))

    def test_old_reset_code_invalidated_after_resend(self):
        from apps.accounts.utils import create_and_send_otp

        self.client.post(
            reverse("accounts:forgot_password"), {"email": "resetuser@example.com"}
        )
        old_otp = EmailOTP.objects.filter(
            user=self.user, purpose="reset_password"
        ).latest("created_at")

        create_and_send_otp(self.user, "reset_password")

        response = self.client.post(
            reverse("accounts:reset_password"),
            {
                "code": old_otp.code,
                "new_password1": "NewStrongPass1!",
                "new_password2": "NewStrongPass1!",
            },
        )
        self.assertContains(response, "no longer valid")


# What this does: self.client simulates a browser making real requests to your views, without needing an actual browser. mail.outbox captures "sent" emails in memory during tests (Django auto-switches to a test email backend). Each test method is one specific scenario — register, verify correct/wrong/used code, resend invalidation, password reset, reset resend invalidation.

# Save it, then run:
# uv run python manage.py test apps.accounts.tests
