from django.shortcuts import render
from django.shortcuts import redirect


from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound
from .models import DATABASE

from logic.services import filtering_category
from logic.services import view_in_cart, add_to_cart, remove_from_cart, filter_same_category


def cart_view(request):
    if request.method == "GET":
        data = view_in_cart()  # TODO Вызвать ответственную за это действие функцию
        if request.GET.get("format") == 'JSON':
            return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                     'indent': 4})

        products = []  # Список продуктов
        for product_id, quantity in data['products'].items():
            product = DATABASE[product_id]  # Получение информацию о продукте из DATABASE по его product_id
            product["quantity"] = quantity  # Запись в словарь product текущее значение товара в корзине
            product["price_total"] = f"{quantity * product['price_after']:.2f}"  # добавление общей цены позиции с ограничением в 2 знака
            products.append(product)

        return render(request, "store/cart.html", context={"products": products})


def cart_add_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(id_product)  # TODO Вызвать ответственную за это действие функцию и передать необходимые параметры
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в корзину"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в корзину"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def cart_del_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(id_product)  # TODO Вызвать ответственную за это действие функцию и передать необходимые параметры
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из корзины"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из корзины"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def products_page_view(request, page: str | int) -> HttpResponse:
    if request.method == 'GET':
        if isinstance(page, str):
            for data in DATABASE.values():
                if data.get('html') == page:
                    # with open(f'store/products/{page}.html', encoding='utf-8') as f:
                    #     html_page = f.read()
                    #     return HttpResponse(html_page)
                    list_products = filter_same_category(data, DATABASE)
                    return render(request, "store/product.html",
                                  context={'product': data,
                                           'products_same_category': list_products})
        elif isinstance(page, int):
            data = DATABASE.get(str(page))
            if data:
                # with open(f'store/products/{data.get("html")}.html', encoding='utf-8') as f:
                #     html_page = f.read()
                #     return HttpResponse(html_page)
                list_products = filter_same_category(data, DATABASE)
                return render(request, "store/product.html",
                              context={'product': data,
                                       'products_same_category': list_products})
        return HttpResponse(status=404)


def products_view(request) -> JsonResponse | HttpResponseNotFound:
    if request.method == "GET":
        # Обработка id из параметров запроса (уже было реализовано ранее)
        if id_product := request.GET.get("id"):
            if data := DATABASE.get(id_product):
                return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                             'indent': 4})
            return HttpResponseNotFound("Данного продукта нет в базе данных")

        # Обработка фильтрации из параметров запроса
        category_key = request.GET.get("category")  # Считали 'category'
        if ordering_key := request.GET.get("ordering"):  # Если в параметрах есть 'ordering'
            reverse = request.GET.get("reverse")
            if reverse and reverse.lower() == 'true':  # Если в параметрах есть 'ordering' и 'reverse'=True
                # Использовать filtering_category и провести фильтрацию с параметрами category, ordering, reverse=True
                data = filtering_category(DATABASE, category_key, ordering_key, True)
            else:  # Если не обнаружили в адресной строке ...&reverse=true , значит reverse=False
                data = filtering_category(DATABASE, category_key, ordering_key)  # Использовать filtering_category и провести фильтрацию с параметрами category, ordering, reverse=False
        else:
            data = filtering_category(DATABASE, category_key)  # Использовать filtering_category и провести фильтрацию с параметрами category
        # В этот раз добавляем параметр safe=False, для корректного отображения списка в JSON
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False,
                                                                 'indent': 4})


# def products_view(request) -> JsonResponse|HttpResponseNotFound:
#     if request.method == "GET":
#         data = DATABASE.copy()
#         product_id = request.GET.get('id')
#         if product_id is not None:
#             data = [product for product in DATABASE.values() if product.get('id') == int(product_id)]
#             if not data:
#                 return HttpResponseNotFound("Данного продукта нет в базе данных")
#         return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


def shop_view(request):
    if request.method == "GET":
        # with open('store/shop.html', encoding="utf-8") as f:
            # data = f.read()  # Читаем HTML файл
        # return HttpResponse(data)  # Отправляем HTML файл как ответ

        # Обработка фильтрации из параметров запроса
        category_key = request.GET.get("category")

        if ordering_key := request.GET.get("ordering"):
            if request.GET.get("reverse") in ('true', 'True'):
                data = filtering_category(DATABASE, category_key, ordering_key, True)
            else:
                data = filtering_category(DATABASE, category_key, ordering_key)
        else:
            data = filtering_category(DATABASE, category_key)

        return render(request, 'store/shop.html',
                      context={"products": data,
                               "category": category_key})


def coupon_check_view(request, coupon):
    # DATA_COUPON - база данных купонов: ключ - код купона (name_coupon); значение - словарь со значением скидки в процентах и
    # значением действителен ли купон или нет
    DATA_COUPON = {
        "coupon": {
            "value": 10,
            "is_valid": True},
        "coupon_old": {
            "value": 20,
            "is_valid": False},
    }
    if request.method == "GET":
        # TODO Проверьте, что купон есть в DATA_COUPON, если он есть, то верните JsonResponse в котором по ключу "discount"
        # получают значение скидки в процентах, а по ключу "is_valid" понимают действителен ли купон или нет (True, False)
        # TODO Если купона нет в базе, то верните HttpResponseNotFound("Неверный купон")

        if coupon in DATA_COUPON:
            data_coupon = {'discount': DATA_COUPON.get(coupon).get('value'),
                           'is_valid': DATA_COUPON.get(coupon).get('is_valid')}
            return JsonResponse(data_coupon, json_dumps_params={'ensure_ascii': False, 'indent': 4})

        return HttpResponseNotFound("Неверный купон")

def delivery_estimate_view(request):
    # База данных по стоимости доставки. Ключ - Страна; Значение словарь с городами и ценами;
    # Значение с ключом fix_price применяется, если нет города в данной стране

    DATA_PRICE = {
        "Россия": {
            "Москва": {"price": 90},
            "Санкт-Петербург": {"price": 70},
            "fix_price": 120,
        },
    }
    if request.method == "GET":
        data = request.GET
        country = data.get('country')
        city = data.get('city')
        # TODO Реализуйте логику расчёта стоимости доставки, которая выполняет следующее:
        # Если в базе DATA_PRICE есть и страна (country) и существует город(city), то вернуть
        # JsonResponse со словарём, {"price": значение стоимости доставки}
        # Если в базе DATA_PRICE есть страна, но нет города, то вернуть
        # JsonResponse со словарём, {"price": значение фиксированной стоимости доставки}
        # Если нет страны, то вернуть HttpResponseNotFound("Неверные данные")

        if country not in DATA_PRICE:
            return HttpResponseNotFound("Неверные данные")

        if city in DATA_PRICE[country]:
            return JsonResponse({"price": DATA_PRICE[country][city].get("price")})

        return JsonResponse({"price": DATA_PRICE[country].get("fix_price")})


def cart_buy_now_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(id_product)
        if result:
            return redirect("store:cart_view")
            # return cart_view(request)

        return HttpResponseNotFound("Неудачное добавление в корзину")


def cart_remove_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(id_product)
        if result:
            return redirect("store:cart_view")

        return HttpResponseNotFound("Неудачное удаление из корзины")
