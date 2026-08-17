from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Handle a Google login when the email belongs to an existing
        unverified pending registration.
        """
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get("email")

        if not email:
            return

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return

        # Only automatically complete an unverified pending account.
        if not user.is_email_verified:
            user.is_email_verified = True
            user.is_active = True
            user.save(
                update_fields=[
                    "is_email_verified",
                    "is_active",
                ]
            )

            sociallogin.connect(request, user)
