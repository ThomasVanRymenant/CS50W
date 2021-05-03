import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from .models import User, Post, Follow

from .forms import createPostForm


def index(request):

    # get all posts
    posts = Post.objects.all().order_by('-created_date')

    # paginate the posts and get the relevant page
    page_obj = None
    multi_page = None
    if posts:
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        multi_page = paginator.num_pages > 1
    
    return render(request, "network/index.html", {
        "page_title": "All posts",
        "createPostForm": createPostForm,
        "page_obj": page_obj,
        "multi_page": multi_page,
        "no_posts_message": "Nobody has shared a post yet"
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html", {
            "page_title": 'Log in'
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name =request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Account name already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html", {
            "page_title": 'Register'
        })


def profile(request, username):

    # try to get the user who's profile wants to be visited
    try:
        user_to_visit = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return render(request, "network/profile.html", {
            "page_title": "Who??",
            "profile": None,
            "requested_user_username": username
        })

    posts = user_to_visit.posts.all().order_by("-created_date")

    # paginate the user's posts
    page_obj = None
    multi_page = None
    if posts:
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        multi_page = paginator.num_pages > 1

    if request.user.is_authenticated:
        is_followed = request.user.following.filter(followed_user=user_to_visit).exists()
    else:
        is_followed = None

    return render(request, "network/profile.html", {
        "page_title": f"{user_to_visit.first_name} {user_to_visit.last_name}",
        "profile": user_to_visit,
        "is_followed": is_followed,
        "page_obj": page_obj,
        "multi_page": multi_page,
        "no_posts_message": "Not shared any posts yet"
    })


@login_required
def following(request):
    """return the posts from users whom are being followed by the requesting user"""
   
    # retreive all posts (if any) of all followed users (if any)
    # Note: done in a "hacky way", in an effort to still be able to call the "order_by"-method of the resulting set
    followed_relations = User.objects.get(pk=request.user.id).following.all()
    posts_exists = False
    posts = None
    page_obj = None
    multi_page = None
    no_posts_message = None
    if followed_relations:

        for rel in followed_relations:
            if posts_exists:
                # add queryset (with "+=" or merge "|" operator)
                posts += rel.followed_user.posts.all()
            else:
                posts = rel.followed_user.posts.all()
                posts_exists = True

        if posts_exists:
            posts = posts.order_by('-created_date')
            # paginate the user's posts and get the relevant page
            paginator = Paginator(posts, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            multi_page = paginator.num_pages > 1
        else:
            # make sure an appropriate message can be rendered in template (should there be no posts to pass to template)
            no_posts_message = "The people you're following haven't shared any posts yet"

    else:
        # make sure an appropriate message can be rendered in template (should user not be following any other users)
        no_posts_message = "You are currently not following anybody"

    return render(request, "network/index.html", {
        "page_title": "Following",
        "createPostForm": createPostForm,
        "page_obj": page_obj,
        "multi_page": multi_page,
        "no_posts_message": no_posts_message
    })
    

@login_required
def create_post(request):
    """create a new post"""

    if request.method == "POST":
        # save submitted form
        new_post_form = createPostForm(request.POST)

        if new_post_form.is_valid():

            # isolate data from the 'cleaned' version of form data
            content = new_post_form.cleaned_data["content"]

            # create & store new post
            new_post = Post(content=content, creator=request.user)
            new_post.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            
            # make sure submitted form gets re-rendered
            return render(request, "network/index.html", {
                "page_title": "All posts",
                "message": 'Something went wrong. Please try again later',
                "createPostForm": new_post_form,
                "posts": Post.objects.all().order_by('-created_date'),
                "no_posts_message": "Nobody has shared a post yet"
            })   


# AJAX route
def toggle_follow(request):
    """follow or unfollow another user"""

    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "user_is_authenticated": False
        }, status = 401)

    # create or delete a following-relationship
    if request.method == "PUT":

        # get user to follow/unfollow
        data = json.loads(request.body)
        user_id = data["id"]
        user = User.objects.get(id=user_id)

        # try to unfollow user, except if user is not followed, then follow user
        try:
            follow_relation = Follow.objects.get(followed_user=user_id, follower=request.user.id)
            follow_relation.delete()
        except ObjectDoesNotExist:
            new_following_rel = Follow(followed_user=user, follower=request.user)
            new_following_rel.save()
        
        return JsonResponse({
            "success": True
        }, status = 201)

    # follow/unfollow must be via PUT request
    else:
        return JsonResponse({
            "success": False,
            "error": "PUT request required."
        }, status=400)


# AJAX route
def edit_post(request):
    """return a post's content, or saves a post's new content"""

    if not request.user.is_authenticated:
            return JsonResponse({"success": False, "user_is_authenticated": False}, status = 401)
    
    if request.method == 'POST':

        # get sent data
        data = json.loads(request.body)
        post_id = data["postId"]
        content = data["content"]

        # make sure the post exists
        try:
            post_to_edit = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "The post that was requested to be edited couldn't be found"
            }, status = 409)

        # make sure the requesting user is authorized to edit the post
        if request.user.id != post_to_edit.creator.id:
            return JsonResponse({
                "success": False,
                "error": "Unauthorized request to edit a post of another user"
            }, status = 409)
        
        # update the post's content
        post_to_edit.content = content
        post_to_edit.save()

        return JsonResponse({
            "success": True
        }, status = 201)

    else:
        return JsonResponse({
            "succes": False,
            "error": 'POST request required'
        }, status = 400)


# AJAX route
def toggle_like(request):
    """save a user's like or dislike of a post"""

    if not request.user.is_authenticated:
            return JsonResponse({"success": False, "user_is_authenticated": False}, status = 401)
    
    if request.method == 'PUT':
        
        data = json.loads(request.body)
        post_id = data['post_id']

        # try to get the post
        try:
            post = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            return JsonResponse({"success": False}, status = 409)

        # 'toggle' the user's liking of the post (based on whether he/she is already among the post's likers or not)
        if request.user in post.likers.all():
            # remove user from the post's likers
            post.likers.remove(request.user)
            liked_or_unliked = 'unliked'
        else:
            # add user to the post's likers
            post.likers.add(request.user)
            liked_or_unliked = 'liked'

        return JsonResponse({
            "success": True, 
            'liked_or_unliked': liked_or_unliked
        }, status = 201)

    else:
        return JsonResponse({
            "success": False,
            "error": "PUT request required."
        }, status=400)