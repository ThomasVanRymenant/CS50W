from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class User(AbstractUser):
    pass


class Category(models.Model):
    """a model that represents a category. Properties: name"""

    name = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.id}: {self.name}"


class Listing(models.Model):
    """A model that represents a Listing.
    Properties: title, description, starting_bid, category, image_url,
    is_active, winner, creator, creationDateTime, highest_bid, watchers"""

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=600)
    starting_bid = models.FloatField()
    category = models.ForeignKey(Category, null=True, default=None, on_delete=models.SET_NULL, related_name="listings")
    image_url = models.CharField(max_length=255, null=True, default=None)
    is_active = models.BooleanField(default=True)
    creationDateTime = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    winner = models.OneToOneField(User, on_delete=models.SET("Winners's account got deleted"), null=True, default=None, related_name="auctions_won")
    highest_bid = models.OneToOneField('Bid', null=True, default=None, on_delete=models.SET_NULL)
    watchers = models.ManyToManyField(User, blank=True, related_name='watching')

    def __str__(self):
        return f"{self.id}: {self.title}"


class Bid(models.Model):
    """a model that represents a bid. Properties: amount, bidder, auction, date"""

    amount = models.FloatField()
    bidder = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="bids")
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.bidder} bid {self.amount} on {self.auction}"


class Comment(models.Model):
    """a model that represents a bid. Properties: comment, commentator, listing, date"""

    comment = models.TextField(max_length=350)
    commentator = models.ForeignKey(User, on_delete=models.SET("Unknown User"), related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: comment on: {self.listing}"