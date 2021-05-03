
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createpost", views.create_post, name="create_post"),
    path("editPost", views.edit_post, name="edit_post"),
    path("following", views.following, name="following"),
    path("profile/<username>", views.profile, name="profile"),
    path("follow", views.toggle_follow, name="toggle_follow"),
    path("like", views.toggle_like, name="toggle_like")
]
