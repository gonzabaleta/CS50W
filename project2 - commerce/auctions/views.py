from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Listing, Category

from .models import User


def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class CreateListingForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=512)
    starting_bid = forms.DecimalField(decimal_places=2, max_digits=20)
    image_url = forms.CharField(max_length=256)
    category = forms.CharField(max_length=32)


def create_listing(request):
    message = None
    error = None
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():

            try:
                category = Category.objects.get(
                    name=form.cleaned_data['category'])
            except Category.DoesNotExist:
                category = None

            if not category:
                category = Category(name=form.cleaned_data['category'])
                category.save()

            listing = Listing(author=request.user,
                              title=form.cleaned_data['title'], description=form.cleaned_data['description'], starting_bid=form.cleaned_data['starting_bid'], image_url=form.cleaned_data['image_url'], category=category)

            listing.save()
            message = "Listing successfully created"

        else:
            error = "Invalid Listing data"

    return render(request, "auctions/create_listing.html", {
        "form": CreateListingForm(),
        "message": message,
        "error": error
    })
