from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Listing, Category

from .models import User


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


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


def single_listing(request, listing_id):
    watchlist_added = request.GET.get('w', '')
    watchlist_msg = None
    if watchlist_added:
        watchlist_msg = "Item added to watchlist successfully"
    watchlist_removed = request.GET.get('r', '')
    if watchlist_removed:
        watchlist_msg = "Item removed from watchlist"

    listing = Listing.objects.get(id=listing_id)

    try:
        is_in_watchlist = request.user.watchlist.get(id=listing.id)
    except Listing.DoesNotExist:
        is_in_watchlist = None

    return render(request, 'auctions/single_listing.html', {"listing": listing, 'watchlist_msg': watchlist_msg, 'is_in_watchlist': is_in_watchlist})


def watchlist(request):
    if request.method == "POST" and request.POST['method'] == 'POST':
        listing_id = int(request.POST['listing_id'])
        listing = Listing.objects.get(id=listing_id)
        request.user.watchlist.add(listing)
        return HttpResponseRedirect(reverse('single_listing', args=[listing_id]) + "?w=true")
    if request.method == "POST" and request.POST['method'] == "DELETE":
        listing_id = int(request.POST['listing_id'])
        listing = Listing.objects.get(id=listing_id)
        request.user.watchlist.remove(listing)
        print('removing')
        return HttpResponseRedirect(reverse('single_listing', args=[listing_id]) + "?r=true")
    elif request.method == "GET":
        watchlist = request.user.watchlist.all()
        return render(request, 'auctions/watchlist.html', {"watchlist": watchlist})
