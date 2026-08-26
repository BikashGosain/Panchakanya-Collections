from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "city",
            "profile_picture",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = None
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

    def clean_email(self):
        email = self.cleaned_data["email"]

        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            # Allow the same pending/unverified account to be updated.
            if (
                self.instance.pk
                and existing_user.pk == self.instance.pk
                and not existing_user.is_email_verified
            ):
                return email

            raise forms.ValidationError("A user with this email already exists.")

        return email


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "city",
            "profile_picture",
        ]
        widgets = {
            "profile_picture": forms.FileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
        }
