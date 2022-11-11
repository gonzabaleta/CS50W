from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<str:listing_id>", views.single_listing, name="single_listing"),
    path('watchlist', views.watchlist, name="watchlist"),
    path('categories', views.categories, name="categories"),
    path('categories/<str:category_id>',
         views.single_category, name="single_category")
]
