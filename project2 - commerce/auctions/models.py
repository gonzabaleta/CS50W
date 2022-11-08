from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


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


class Bid(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(decimal_places=2, max_digits=20)


class Comment(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
