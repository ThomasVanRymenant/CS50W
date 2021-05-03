from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories_view, name="categories"),
    path("c/<str:category>", views.category_listings, name="category_listings"),
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("newlisting", views.create_listing, name="createlisting"),
    path("mylistings", views.my_listings, name="my_listings"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("watchlistadd/<int:listing_id>", views.watchlist_add, name="watchlist_add"),
    path("watchlistremove/<int:listing_id>", views.watchlist_remove, name="watchlist_remove"),
    path("placebid/<int:listing_id>", views.bid, name='bid'),
    path("close/<int:listing_id>", views.close_auction, name="close_auction"),
    path("comment/<int:listing_id>", views.add_comment, name='add_comment')
]
