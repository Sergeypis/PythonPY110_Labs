from django.shortcuts import render


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
