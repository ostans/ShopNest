from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from .forms import (
    AddressForm,
    BaseRegisterForm,
    BecomeSellerForm,
    LoginForm,
    SellerRegisterForm,
)
from .models import Address, SellerProfile


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
            user.role = "seller"
            user.save(update_fields=["role"])
            login(request, user)
            messages.success(request, "You have successfully registered as seller")
            return redirect("seller-dashboard")
        else:
            messages.error(request, "Registration failed", extra_tags="danger")
    else:
        form = SellerRegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in")
            return redirect("customer-dashboard")
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
def become_seller_view(request):
    if request.user.role == "seller":
        return redirect("seller-dashboard")

    if request.method == "POST":
        form = BecomeSellerForm(request.POST)
        if form.is_valid():
            seller_profile, created = SellerProfile.objects.get_or_create(
                user=request.user
            )
            seller_profile.national_id = form.cleaned_data["national_id"]
            seller_profile.address = form.cleaned_data["address"]
            seller_profile.bio = form.cleaned_data["bio"]
            seller_profile.save()

            request.user.role = "seller"
            request.user.save(update_fields=["role"])

            messages.success(request, "You have successfully become a seller.")
            return redirect("seller-dashboard")
    else:
        form = BecomeSellerForm()

    return render(request, "accounts/become_seller.html", {"form": form})


@login_required
def seller_dashboard_view(request):
    profile = getattr(request.user, "seller_profile", None)
    if not profile:
        messages.error(request, "You are not a seller", extra_tags="danger")
        return redirect("become-seller")

    stores = profile.stores.all() if hasattr(profile, "stores") else []
    return render(
        request,
        "accounts/seller_dahboard.html",
        {"profile": profile, "stores": stores, "user": request.user},
    )


@login_required
def address_list_view(request):
    address_list_view = Address.objects.filter(user=request.user)
    return render(
        request, "accounts/address_list.html", {"addresses": address_list_view}
    )


@login_required
def address_create_view(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address saved.")
            return redirect("address-list")
    else:
        form = AddressForm()
    return render(request, "accounts/address_form.html", {"form": form})


@login_required
def address_update_view(request, pk):
    address = Address.objects.filter(user=request.user).get(pk=pk)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated.")
            return redirect("address-list")
    else:
        form = AddressForm(instance=address)
    return render(request, "accounts/address_form.html", {"form": form})


@login_required
def address_delete_view(request, pk):
    address = Address.objects.filter(user=request.user).get(pk=pk)
    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted.")
        return redirect("address-list")
    return render(request, "accounts/address_confirm_delete.html", {"address": address})
