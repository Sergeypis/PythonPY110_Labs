from django.shortcuts import render, redirect
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse, HttpResponseRedirect
from store.models import DATABASE
from logic.services import (view_in_wishlist,
                            add_to_wishlist,
                            remove_from_wishlist)


@login_required(login_url='login:login_view')
def wishlist_view(request) -> HttpResponse:
    """
    Загрузка шаблона страницы избранного с товарами зарегистрированного пользователя.

    :param request: Объект запроса.
    :return: HttpResponse, как результат функции render с шаблоном избранного с товарами пользователя в контексте.
    """
    if request.method == 'GET':
        current_user = get_user(request).username
        user_wishlist = view_in_wishlist(request).get(current_user)

        products = []
        for product_id in user_wishlist['products']:
            product = DATABASE[product_id]
            products.append(product)
        return render(request, 'wishlist/wishlist.html',
                      context={'products': products})


def wishlist_remove_view(request, id_product: str) -> HttpResponseNotFound | HttpResponseRedirect:
    """
    Удаление продукта из избранного и перезагрузка страницы.

    :param request: Объект запроса.
    :param id_product: Идентификационный номер продукта в виде строки.
    :return: -Редирект на страницу Избранное.
             -Сообщение об ошибке.
    """
    if request.method == "GET":
        result = remove_from_wishlist(request, id_product)
        if result:
            return redirect("wishlist:wishlist_view")

        return HttpResponseNotFound("Неудачное удаление из избранного")


@login_required(login_url='login:login_view')
def wishlist_add_json(request, id_product: str) -> JsonResponse:
    """
    Добавление продукта в БД избранное и возвращение информации об успехе или неудаче в JSON.

    :param request: Объект запроса.
    :param id_product: Идентификационный номер продукта в виде строки.
    :return: Сообщение об успехе или неудаче в JSON.
    """
    if request.method == "GET":
        result = add_to_wishlist(request, id_product)  # добавляет продукт в избранное
        if result:
            return JsonResponse({'answer': "Продукт успешно добавлен в избранное"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({'answer': "Неудачное добавление в избранное"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def wishlist_del_json(request, id_product: str) -> JsonResponse:
    """
    Удаление продукта из БД избранного и возвращение информации об успехе или неудаче в JSON.

    :param request: Объект запроса.
    :param id_product: Идентификационный номер продукта в виде строки.
    return: Сообщение об успехе или неудаче в JSON.
    """
    if request.method == "GET":
        result = remove_from_wishlist(request, id_product)  # удаляет продукт из избранного
        if result:
            return JsonResponse({'answer': "Продукт успешно удалён из избранного"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({'answer': "Неудачное удаление из избранного"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def wishlist_json(request) -> JsonResponse:
    """
    Просмотр всех продуктов в избранном для пользователя и возвращение этого в JSON для изменения статуса сердечек.

    :param request: Объект запроса.
    return: -Список продуктов в избранном пользователя в JSON.
            -Сообщение об ошибке в JSON.
    """
    if request.method == "GET":
        if current_user := get_user(request).username:
            data = view_in_wishlist(request)[current_user]  # данные о списке товаров в избранном у пользователя
            if data:
                return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

        return JsonResponse({'answer': "Пользователь не авторизирован"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})
