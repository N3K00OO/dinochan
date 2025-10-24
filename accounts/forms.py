"""Forms related to authentication flows."""
from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginForm(AuthenticationForm):
    """Styled login form used across the site."""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Password",
            }
        )
    )


class RegistrationForm(UserCreationForm):
    """Public user registration form."""

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Confirm Password",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username",)
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "placeholder": "Username",
                }
            )
        }


class AdminCreationForm(UserCreationForm):
    """Form used by administrators to create fellow admins."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                existing_classes = widget.attrs.get("class", "")
                if "custom-select" not in existing_classes.split():
                    widget.attrs["class"] = (existing_classes + " custom-select").strip()

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl border border-white/30 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl border border-white/30 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Confirm Password",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username",)
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/30 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "placeholder": "Username",
                }
            )
        }

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user
