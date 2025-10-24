"""Authentication views."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView

from .forms import LoginForm, RegistrationForm


class AuthLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm

    def get_success_url(self) -> str:
        return reverse("home")


class AuthLogoutView(LoginRequiredMixin, View):
    """Log out the current user and redirect them to the login page."""

    success_url = reverse_lazy("auth:login")

    def _logout(self, request: HttpRequest) -> None:
        logout(request)
        messages.success(request, "You have been logged out successfully.")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self._logout(request)
        return redirect(self.success_url)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = "auth/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("auth:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registration successful. Please log in.")
        return super().form_valid(form)
