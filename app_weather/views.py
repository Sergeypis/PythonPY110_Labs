from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import requests
from django.http import JsonResponse
from .models import DIRECTION_TRANSFORM


def current_weather(lat, lon):
    """
    Описание функции, входных и выходных переменных
    """
    token = '29e0b288a4ef408a8c4201243240305'  # Вставить ваш токен
    url = f"https://api.weatherapi.com/v1/current.json?key={token}&q={lat},{lon}"  # Запрос на https://api.weatherapi.com
    # headers = {"X-Yandex-API-Key": f"{token}"}
    # response = requests.get(url, headers=headers)
    response = requests.get(url)
    data = response.json()

    result = {
        'city': data['location']['name'],
        # 'time': datetime.fromtimestamp(data['fact']['uptime']).strftime("%H:%M"),
        'time': data['current']['last_updated'],
        'temp': data['current']['temp_c'],  # TODO Реализовать вычисление температуры из данных полученных от API
        'feels_like_temp': data['current']['feelslike_c'],  # TODO Реализовать вычисление ощущаемой температуры из данных полученных от API
        'pressure': round(data['current']['pressure_mb'] * 0.75, 1),  # TODO Реализовать вычисление давления из данных полученных от API
        'humidity': data['current']['humidity'],  # TODO Реализовать вычисление влажности из данных полученных от API
        'wind_speed': round(data['current']['wind_kph'] / 3.6, 1),  # TODO Реализовать вычисление скорости ветра из данных полученных от API
        'wind_gust': round(data['current']['gust_kph'] / 3.6, 1),  # TODO Реализовать вычисление скорости порывов ветка из данных полученных от API
        'wind_dir': DIRECTION_TRANSFORM.get(data['current']['wind_dir'].lower()),
    }

    return result


def my_view(request):
    if request.method == "GET":
        data = current_weather(59.93, 30.31)
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 4})
