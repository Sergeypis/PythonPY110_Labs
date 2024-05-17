from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound
from .models import DATABASE


def products_page_view(request, page: str | int) -> HttpResponse:
    if request.method == 'GET':
        if isinstance(page, str):
            for data in DATABASE.values():
                if data.get('html') == page:
                    with open(f'store/products/{page}.html', encoding='utf-8') as f:
                        html_page = f.read()
                        return HttpResponse(html_page)
        elif isinstance(page, int):
            data = DATABASE.get(str(page))
            if data:
                with open(f'store/products/{data.get("html")}.html', encoding='utf-8') as f:
                    html_page = f.read()
                    return HttpResponse(html_page)
        return HttpResponse(status=404)


def products_view(request) -> JsonResponse|HttpResponseNotFound:
    if request.method == "GET":
        data = DATABASE.copy()
        product_id = request.GET.get('id')
        if product_id is not None:
            data = [product for product in DATABASE.values() if product.get('id') == int(product_id)]
            if not data:
                return HttpResponseNotFound("Данного продукта нет в базе данных")
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


def shop_view(request):
    if request.method == "GET":
        with open('store/shop.html', encoding="utf-8") as f:
            data = f.read()  # Читаем HTML файл
        return HttpResponse(data)  # Отправляем HTML файл как ответ