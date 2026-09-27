from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import BaseRegisterForm, SellerRegisterForm, LoginForm
from .models import SellerProfile


def customer_register_view(request):
    if request.method == "POST":
        form = BaseRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You have successfully registered.")
            return redirect("home")
        else:
            messages.error(
                request,
                "Registration failed. Please correct the errors below.",
                extra_tags="danger",
            )
    else:
        form = BaseRegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def seller_register_view(request):
    if request.method == "POST":
        form = SellerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            SellerProfile.objects.create(
                user=user,
                national_id=form.cleaned_data["national_id"],
                bio=form.cleaned_data["bio"],
            )
            login(request=user)
            messages.success(request, "You have successfully registered as seller")
            return redirect("seller_dashboard")
        else:
            messages.error(request, "Registration failed", extra_tags="danger")
    else:
        form = SellerRegisterForm()
    return render(request, "accounts/seller_register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in")
            return redirect("home")
        else:
            messages.error(request, "Invalid phone number or password")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logget out", extra_tags="Info")
    return redirect(reverse("home"))


@login_required
def customer_dashboard_view(request):
    profile = request.user.customer_profile
    return render(request, "accounts/customer_dashboard.html", {"profile": profile})


@login_required
def seller_dashboard_view(request):
    profile = request.user.seller_profile
    if not profile:
        messages.error(request, "You are not a seller", extra_tags="danger")
        return redirect("seller-register")
    stores = profile.stores.all()
    return render(
        request, "accounts/seller_dahboard.html", {"profile": profile, "stores": stores}
    )
