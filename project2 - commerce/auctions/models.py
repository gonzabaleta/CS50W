from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=32)


class Listing(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=20)
    image_url = models.CharField(max_length=256, blank=True, null=True)
    category = models.ForeignKey(
        Category, models.SET_NULL, blank=True, related_name="listings", null=True)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} | {self.title} | {self.author.username}"


class Bid(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(decimal_places=2, max_digits=20)

    def __str__(self):
        return f"{self.user.username} bid ${self.price} on '{self.listing.title}'"


class Comment(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=512, default="")

    def __str__(self):
        return f"{self.author.username} on '{self.listing.title}'"
