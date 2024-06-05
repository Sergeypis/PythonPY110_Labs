"""
URL configuration for app wishlist.

"""

from django.urls import path
from wishlist.views import wishlist_view


app_name = 'wishlist'

urlpatterns = [
    path('wishlist/', wishlist_view, name='wishlist_view'),
]


