from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Category, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    """shows active listings, ordered by date (newest->oldest)"""

    # direct user to the page where active listings are shown, ordered by date (newest->oldest)
    return render(request, "auctions/index.html", {
        "page_link": "active listings",
        "page_header": "Active Listings",
        "listings": Listing.objects.filter(is_active=True).order_by('-creationDateTime')
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
            next_url = request.POST.get('next')
            if next_url != "None":
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(reverse("index"))

        else:
            # make a message which can be shown in the login-template
            messages.add_message(request, messages.ERROR, 'Invalid username and/or password.')
            return render(request, "auctions/login.html")
    else:
        messages.add_message(request, messages.SUCCESS, 'Yay! Logged in successfully')
        return render(request, "auctions/login.html", {
            "next": request.GET.get('next')
        })


def logout_view(request):
    try:
        user_was = request.user
    except ObjectDoesNotExist:
        user_was = False
    logout(request)

    # make a message which can be displayed after redirecting the user to the (in the case of this app:) home-page
    if user_was == False:
        messages.add_message(request, messages.INFO, "You're a rebel aren't you...")
    else:
        messages.add_message(request, messages.INFO, 'You are logged out successfully')
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.add_message(request, messages.ERROR, 'Passwords must match !')
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Username already taken.')
            return render(request, "auctions/register.html")
        login(request, user)
        messages.add_message(request, messages.SUCCESS, 'Congrats! You are now registered')
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing_view(request, listing_id):
    """shows a requested listing with all its relevant information"""

    if request.method == "GET":

        # try to retreive the requested listing
        try:
            requested_listing = Listing.objects.get(pk=listing_id)
        except ObjectDoesNotExist:
            requested_listing = None

        comments = ''
        comments_amount = ''

        # check if user has the listing in his watchlist
        listing_is_watched = False
        if requested_listing:
            user_as_watcher = requested_listing.watchers.filter(pk=request.user.id)
            if user_as_watcher: # == if the watching user was found between listing's watchers
                listing_is_watched = True

            # additionnaly, get all listing's comments to pass to html
            comments = requested_listing.comments.all().order_by('-date')
            comments_amount = len(comments)

        # render page with listing (or a template-provided error if the listing doesn't exist/is None)
        return render(request, "auctions/listing.html", {
            "listing": requested_listing,
            "comments": comments,
            "comments_amount": comments_amount,
            "listing_is_watched": listing_is_watched,
            "bidForm": BidForm,
            "commentForm": CommentForm
        })


@login_required
def create_listing(request):
    """allow a logged-in user to create a new listing"""

    if request.method == "POST":

        # save data of the posted form in new_listing_form
        new_listing_form = ListingForm(request.POST)

        # check if form data is valid (within bounderies of what it is expected to be)
        if new_listing_form.is_valid():

            # isolate data from the 'cleaned' version of form data
            title = new_listing_form.cleaned_data["title"]
            description = new_listing_form.cleaned_data["description"]
            starting_bid = new_listing_form.cleaned_data["starting_bid"]
            image_url = new_listing_form.cleaned_data["image_url"]
            chosen_category_id = new_listing_form.cleaned_data["category"]

            # check if a category was provided (note to self: could be done more efficiently??)
            category = None
            if chosen_category_id: # if a category was selected
                category = Category.objects.get(pk=chosen_category_id)

            # create and save a new listing
            new_listing = Listing(title=title, description=description, category=category, starting_bid=starting_bid, image_url=image_url, creator=request.user)
            new_listing.save()

            # redirect user to the listing function which will render the new listing's page
            messages.add_message(request, messages.SUCCESS, 'Yay! Other users can now see this listing')
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":new_listing.pk}))
        else:
            # catch potential unknown error(s). Re-render form as it was posted and display an error message
            messages.add_message(request, messages.ERROR, 'Something went wrong. Make sure all the required fields are filled in and valid.')
            return render(request, "createlisting.html", {
                "form": new_listing_form
            })
    else:
        return render(request, "auctions/createlisting.html", {
            "form": ListingForm
        })


def categories_view(request):
    """shows all listing categories"""

    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all().order_by('name')
    })


def category_listings(request, category):
    """shows all listings within a requested category"""

    if request.method == "GET":
        return render(request, "auctions/index.html", {
            "page_header": "Listings in: " + category,
            "alt_text": "There are currently no listings here",
            "category": category,
            "listings": Category.objects.get(name=category).listings.all().order_by('-creationDateTime')
        })


@login_required
def watchlist_view(request):
    """shows a logged-in user all the listings that they are currently watching"""

    if request.method == "GET":
        return render(request, "auctions/index.html", {
            "page_header": "Watchlist",
            "alt_text": "Currently empty",
            "listings": User.objects.get(id=request.user.id).watching.all().order_by('-creationDateTime')
        })


@login_required
def watchlist_add(request, listing_id):
    """allows a logged-in user to add a listing to their watchlist"""

    # add listing to user's watchlist (add user to the listing's watchers)
    # important note: this logic doesn't take into consideration that a listing may get deleted between 
    # the time that -the listing-page is rendered- and -a request from the client-side is send to this route-.
    Listing.objects.get(pk=listing_id).watchers.add(request.user)
    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))


@login_required
def watchlist_remove(request, listing_id):
    """allows a logged-in user to remove a listing from their watchlist"""

    # remove listing from user's watchlist (remove user from the listing's watchers)
    # important note: this logic doesn't take into consideration that a listing may get deleted between 
    # the time that -the listing-page is rendered- and -a request from the client-side is send to this route-.
    Listing.objects.get(pk=listing_id).watchers.remove(request.user)
    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))


@login_required
def my_listings(request):
    """allows a logged-in user to view the listings they created"""

    if request.method == "GET":
        return render(request, "auctions/index.html", {
            "page_header": "My auctions",
            "alt_text": "No listings yet",
            "listings": User.objects.get(id=request.user.id).auctions.all().order_by('-creationDateTime')
        })


@login_required
def bid(request, listing_id):
    """allows a logged-in user to place a bid on an auction (if bid is valid)"""

    if request.method == "POST":
        # store posted form in new variable
        new_bid_form = BidForm(request.POST)

        # try to retreive the listing
        try:
            listing = Listing.objects.get(pk=listing_id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

        if new_bid_form.is_valid():
            # get cleaned form data
            placed_bid_amount = new_bid_form.cleaned_data["bid_amount"]

            if listing.starting_bid < placed_bid_amount:
                if listing.highest_bid:
                    if listing.highest_bid.amount < placed_bid_amount:
                        bid_is_valid = True
                    else:
                        bid_is_valid = False
                else:
                    bid_is_valid = True
            else:
                bid_is_valid = False
        else:
            bid_is_valid = False
        
        if bid_is_valid == False:
            # rerender form, with a message
            messages.add_message(request, messages.ERROR, 'Invalid bid. A bid must exceed both the starting bid & all previous bids')
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
        else:
            # if new bid is valid --> create/save it in database and redirect user to the listing's page

            # create & save new bid
            new_bid = Bid(amount=placed_bid_amount, bidder=request.user, auction=listing)
            new_bid.save()

            # set the new bid as the highest bid of the listing
            listing.highest_bid = new_bid
            listing.save()
            
            messages.add_message(request, messages.SUCCESS, 'Congrats! Your bid has been placed')
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))


@login_required
def close_auction(request, listing_id):
    """allows a logged-in user to close one of their created listings. The highest bidder (if any) will be declared as the winner of that auction"""

    # make sure listing exists
    try:
        auction = Listing.objects.get(pk=listing_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

    # check if user has permission to close the auction (if user is the creator)
    if request.user != auction.creator:
        messages.add_message(request, messages.ERROR, 'You are not authorised to close this auction')
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

    # make listing no longer active
    auction.is_active = False

    # make the highest bidder the winner (if any bids have been placed)
    if auction.highest_bid:
        auction.winner = auction.highest_bid.bidder
    auction.save()

    # redirect user to show the listing's page and a message
    messages.add_message(request, messages.SUCCESS, 'The auction has been closed successfully')
    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))


@login_required
def add_comment(request, listing_id):
    """allows a logged in user to place a comment on an active listing"""

    if request.method == "POST":

        # make sure listing exists
        try:
            listing = Listing.objects.get(pk=listing_id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

        # don't allow commenting when listing is inactive (closed)
        if listing.is_active == False:
            messages.add_message(request, messages.INFO, "This listing is closed. No more comments can be made")
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

        # save posted comment-form
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():

            # get cleaned data
            comment_content = comment_form.cleaned_data["comment"]

            # create new comment object
            new_comment = Comment(comment=comment_content, commentator=request.user, listing=listing)
            new_comment.save()

            # add the comment to the listin's comments
            listing.comments.add(new_comment)
            listing.save()

            messages.add_message(request, messages.SUCCESS, "Yay! Your comment has been saved")
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

        else: # rerender listing page with form and display an error message
            messages.add_message(request, messages.ERROR, "A new comment must be between 1-300 characters")

            # check if user has the listing in his watchlist
            listing_is_watched = False
            if listing:
                user_as_watcher = listing.watchers.filter(pk=request.user.id)
                if user_as_watcher: # == if the watching user was found between listing's watchers
                    listing_is_watched = True

            # render page with listing (or a build-in template-error if the listing doesn't exist/is None)
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": listing.comments.all(),
                "listing_is_watched": listing_is_watched,
                "bidForm": BidForm,
                "commentForm": comment_form
            })