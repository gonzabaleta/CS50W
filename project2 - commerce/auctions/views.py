from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Listing, Category, Bid, Comment
from operator import attrgetter
from types import SimpleNamespace
from django.contrib.auth.decorators import login_required

from .models import User


def index(request):
    listings = Listing.objects.filter(is_closed=False)
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


@login_required
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


class PlaceBidForm(forms.Form):
    bid = forms.DecimalField(decimal_places=2, max_digits=20)


class CommentForm(forms.Form):
    text = forms.CharField(max_length=512)


def get_max_bid(listing):
    listing_bids = listing.bids.all()
    if len(listing_bids):
        return max(listing_bids, key=attrgetter('price'))
    else:
        return SimpleNamespace(price=listing.starting_bid, listing=listing, user=None)


@login_required
def place_bid(bid, listing, user):
    if bid < listing.starting_bid:
        return {"error": "Bid must be at least as large as the starting bid"}

    if len(listing.bids.all()) and bid <= get_max_bid(listing).price:
        return {"error": "Bid must be greater than latest bid"}

    bid_save = Bid(price=bid, listing=listing, user=user)
    bid_save.save()
    return {"success": "Bid placed successfully"}


def single_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    bid_message = {"error": None, "success": None}
    if request.method == "POST":
        if "place_bid" in request.POST:
            bid_form = PlaceBidForm(request.POST)
            if bid_form.is_valid():
                bid = float(bid_form.cleaned_data['bid'])
                bid_message = place_bid(bid, listing, request.user)

        if 'close_listing' in request.POST:
            listing.is_closed = True
            listing.save()

        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                text = comment_form.cleaned_data['text']
                comment = Comment(text=text, listing=listing,
                                  author=request.user)
                comment.save()

    watchlist_added = request.GET.get('w', '')
    watchlist_msg = None
    if watchlist_added:
        watchlist_msg = "Item added to watchlist successfully"
    watchlist_removed = request.GET.get('r', '')
    if watchlist_removed:
        watchlist_msg = "Item removed from watchlist"

    try:
        is_in_watchlist = request.user.watchlist.get(id=listing.id)
    except:
        is_in_watchlist = None

    max_bid = get_max_bid(listing)
    if max_bid.user == None:
        max_bid.user = request.user

    return render(request, 'auctions/single_listing.html', {
        "listing": listing,
        "max_bid": max_bid.price,
        'watchlist_msg': watchlist_msg,
        'is_in_watchlist': is_in_watchlist,
        'place_bid_form': PlaceBidForm(),
        'bid_message': bid_message,
        'bid_count': len(listing.bids.all()),
        'is_user_winning': get_max_bid(listing).user == request.user,
        'comment_form': CommentForm(),
        'comments': listing.comments.all()
    })


@login_required
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


def categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {"categories": categories})


def single_category(request, category_id):
    category = Category.objects.get(id=int(category_id))
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/single_category.html", {
        "listings": listings,
        "category": category
    })
