from django.shortcuts import render
from django.contrib.auth import get_user
from django.http import HttpResponse, HttpResponseNotFound
from store.models import DATABASE
from logic.services import (view_in_wishlist,
                            add_to_wishlist,
                            remove_from_wishlist,
                            add_user_to_wishlist)


def wishlist_view(request):
    if request.method == 'GET':
        current_user = get_user(request).username
        user_wishlist = view_in_wishlist(request).get(current_user)

        products = []
        for product_id in user_wishlist['products']:
            product = DATABASE[product_id]
            products.append(product)
        return render(request, 'wishlist/wishlist.html',
                      context={'products': products})

