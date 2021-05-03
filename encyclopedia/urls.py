from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("wiki/<str:title>/edit", views.edit_entry, name="editentry"),
    path("search", views.search, name="search"),
    path("newpage", views.new_entry, name="newentry"),
    path("random", views.random_entry, name="randomentry")
]
