import json
import os

from django.contrib.auth import get_user
from store.models import DATABASE
from random import shuffle


def add_user_to_wishlist(request, username: str) -> None:
    """
    Добавляет пользователя в базу данных избранного, если его там не было.

    :param request: Объект запроса.
    :param username: Имя пользователя
    :return: None
    """
    wishlist_users = view_in_wishlist(request)  # Чтение всей базы избранного

    wishlist = wishlist_users.get(username)  # Получение избранного конкретного пользователя

    if not wishlist:  # Если пользователя до настоящего момента не было в избранном, то создаём его и записываем в базу
        with open('wishlist.json', mode='w', encoding='utf-8') as f:
            wishlist_users[username] = {'products': []}
            json.dump(wishlist_users, f)


def view_in_wishlist(request) -> dict:
    """
    Просматривает содержимое базы данных избранного wishlist.json

    :param request: Объект запроса.
    :return: Содержимое 'wishlist.json'
    """
    if os.path.exists('wishlist.json'):  # Если файл существует
        with open('wishlist.json', encoding='utf-8') as f:
            return json.load(f)

    user = get_user(request).username  # Получаем авторизированного пользователя
    wishlist = {user: {'products': []}}  # Создаём пустое избранное
    with open('wishlist.json', mode='x', encoding='utf-8') as f:  # Создаём файл и записываем туда пустое избранное
        json.dump(wishlist, f)

    return wishlist


def add_to_wishlist(request, id_product: str) -> bool:
    """
    Добавляет продукт в избранное, если в избранном нет такого продукта.

    :param request: Объект запроса.
    :param id_product: Идентификационный номер продукта в виде строки.
    :return: Возвращает True в случае успешного добавления, а False в случае неуспешного добавления(товара по id_product
    не существует).
    """
    wishlist_users = view_in_wishlist(request)
    wishlist = wishlist_users[get_user(request).username]  # получить кизбранное авторизированного пользователя

    if id_product not in wishlist.get('products'):
        if id_product not in DATABASE:
            return False
        else:
            wishlist['products'].append(id_product)

    with open('wishlist.json', mode='w', encoding='utf-8') as f:  # Записываем данные в избранное
        json.dump(wishlist_users, f)

    return True


def remove_from_wishlist(request, id_product: str) -> bool:
    """
    Удаляет позицию продукт из избранного. Если в избранном есть такой продукт, то он удаляется из списка.

    :param request: Объект запроса.
    :param id_product: Идентификационный номер продукта в виде строки.
    :return: Возвращает True в случае успешного удаления, а False в случае неуспешного удаления(товара по id_product
    не существует).
    """
    wishlist_users = view_in_wishlist(request)
    wishlist = wishlist_users[get_user(request).username]

    if id_product not in wishlist.get('products'):
        return False
    else:
        wishlist['products'].remove(id_product)

    with open('wishlist.json', mode='w', encoding='utf-8') as f:
        json.dump(wishlist_users, f)

    return True


def add_user_to_cart(request, username: str) -> None:
    """
    Добавляет пользователя в базу данных корзины, если его там не было.

    :param request: Объект запроса.
    :param username: Имя пользователя
    :return: None
    """
    cart_users = view_in_cart(request)  # Чтение всей базы корзин

    cart = cart_users.get(username)  # Получение корзины конкретного пользователя

    if not cart:  # Если пользователя до настоящего момента не было в корзине, то создаём его и записываем в базу
        with open('cart.json', mode='w', encoding='utf-8') as f:
            cart_users[username] = {'products': {}}
            json.dump(cart_users, f)


def filter_same_category(current_product: dict,
                         database: dict[str, dict]) -> list[dict]:
    """
    Формирует  список продуктов той же категории, что и у выбранного продукта.

    :param current_product: Текущий выбранный продукт.
    :param database: База данны продуктов.
    :return: Список словарей продуктов той же категории
    """
    data = list(filter(lambda x: x.get('category') == current_product.get('category'), database.values()))
    if current_product in data: data.remove(current_product)
    shuffle(data)
    return data[:4]


def view_in_cart(request) -> dict:
    """
    Просматривает содержимое cart.json

    :param request: Объект запроса.
    :return: Содержимое 'cart.json'
    """
    if os.path.exists('cart.json'):  # Если файл существует
        with open('cart.json', encoding='utf-8') as f:
            return json.load(f)

    user = get_user(request).username  # Получаем авторизированного пользователя
    cart = {user: {'products': {}}}  # Создаём пустую корзину
    with open('cart.json', mode='x', encoding='utf-8') as f:  # Создаём файл и записываем туда пустую корзину
        json.dump(cart, f)

    return cart


def add_to_cart(request, id_product: str) -> bool:
    """
    Добавляет продукт в корзину. Если в корзине нет данного продукта, то добавляет его с количеством равное 1.
    Если в корзине есть такой продукт, то добавляет количеству данного продукта + 1.

    :param request: Объект запроса.
    :param id_product: Идентификационный номер продукта в виде строки.
    :return: Возвращает True в случае успешного добавления, а False в случае неуспешного добавления(товара по id_product
    не существует).
    """
    cart_users = view_in_cart(request)
    cart = cart_users[get_user(request).username]  # получить корзину авторизированного пользователя

    # ! Обратите внимание, что в переменной cart находится словарь с ключом products.
    # ! Именно в cart["products"] лежит словарь гдк по id продуктов можно получить число продуктов в корзине.
    # ! Т.е. чтобы обратиться к продукту с id_product = "1" в переменной cart нужно вызвать
    # ! cart["products"][id_product]
    # ! Далее уже сами решайте как и в какой последовательности дальше действовать.

    # Проверьте, а существует ли такой товар в корзине, если нет,
    # то перед тем как его добавить - проверьте есть ли такой id_product товара
    # в вашей базе данных DATABASE, чтобы уберечь себя от добавления несуществующего товара.
    # Если товар существует, то увеличиваем его количество на 1
    # Не забываем записать обновленные данные cart в 'cart.json'. Так как именно из этого файла мы считываем данные и если мы не запишем изменения, то считать измененные данные не получится.

    if id_product not in cart.get('products'):
        if id_product not in DATABASE:
            return False
        else:
            cart['products'][id_product] = 1
    else:
        cart['products'][id_product] += 1

    with open('cart.json', mode='w', encoding='utf-8') as f:  # Записываем данные в корзину
        json.dump(cart_users, f)

    return True


def remove_from_cart(request, id_product: str) -> bool:
    """
    Удаляет позицию продукта из корзины. Если в корзине есть такой продукт, то удаляется ключ в словаре
    с этим продуктом.

    :param request: Объект запроса.
    :param id_product: Идентификационный номер продукта в виде строки.
    :return: Возвращает True в случае успешного удаления, а False в случае неуспешного удаления(товара по id_product
    не существует).
    """
    cart_users = view_in_cart(request)  # Помните, что у вас есть уже реализация просмотра корзины,
    # поэтому, чтобы загрузить данные из корзины, не нужно заново писать код.
    cart = cart_users[get_user(request).username]

    # С переменной cart функции remove_from_cart ситуация аналогичная, что с cart функции add_to_cart
    # Проверьте, а существует ли такой товар в корзине, если нет, то возвращаем False.
    # Если существует товар, то удаляем ключ 'id_product' у cart['products'].
    # Не забываем записать обновленные данные cart в 'cart.json'

    if id_product not in cart.get('products'):
        return False
    else:
        del cart['products'][id_product]

    with open('cart.json', mode='w', encoding='utf-8') as f:  # Записываем данные в корзину
        json.dump(cart_users, f)

    return True


def filtering_category(database: dict[str, dict],
                       category_key: [None, str] = None,
                       ordering_key: [None, str] = None,
                       reverse: bool = False) -> list[dict]:
    """
    Функция фильтрации данных по параметрам

    :param database: База данных. (словарь словарей. При проверке в качестве database будет передаваться словарь DATABASE из models.py)
    :param category_key: [Опционально] Ключ для группировки категории. Если нет ключа, то рассматриваются все товары.
    :param ordering_key: [Опционально] Ключ по которому будет произведена сортировка результата.
    :param reverse: [Опционально] Выбор направления сортировки:
        False - сортировка по возрастанию;
        True - сортировка по убыванию.
    :return: list[dict] список товаров с их характеристиками, попавших под условия фильтрации. Если нет таких элементов,
    то возвращается пустой список
    """
    if category_key is not None:
        result = list(filter(lambda x: x.get('category') == category_key, database.values()))  #  При помощи фильтрации в list comprehension профильтруйте товары по категории (ключ 'category') в продукте database. Или можете использовать

        # обычный цикл или функцию filter. Допустим фильтрацию в list comprehension можно сделать по следующему шаблону
        # [product for product in database.values() if ...] подумать, что за фильтрующее условие можно применить.
        # Сравните значение категории продукта со значением category_key
    else:
        result = [*database.values()]  # Трансформируйте словарь словарей database в список словарей

    if ordering_key is not None:
        # Проведите сортировку result по ordering_key и параметру reverse
        # Так как result будет списком, то можно применить метод sort, но нужно определиться с тем по какому элементу сортируем и в каком направлении
        # result.sort(key=lambda ..., reverse=reverse)
        # Вспомните как можно сортировать по значениям словаря при помощи lambda функции

        result = sorted(result, key=lambda x: x[ordering_key], reverse=reverse)
    return result


if __name__ == "__main__":
    # from store.models import DATABASE

    test = [
        {'name': 'Клубника', 'discount': None, 'price_before': 500.0,
         'price_after': 500.0,
         'description': 'Сладкая и ароматная клубника, полная витаминов, чтобы сделать ваш день ярче.',
         'rating': 5.0, 'review': 200, 'sold_value': 700,
         'weight_in_stock': 400,
         'category': 'Фрукты', 'id': 2, 'url': 'store/images/product-2.jpg',
         'html': 'strawberry'},

        {'name': 'Яблоки', 'discount': None, 'price_before': 130.0,
         'price_after': 130.0,
         'description': 'Сочные и сладкие яблоки - идеальная закуска для здорового перекуса.',
         'rating': 4.7, 'review': 30, 'sold_value': 70, 'weight_in_stock': 200,
         'category': 'Фрукты', 'id': 10, 'url': 'store/images/product-10.jpg',
         'html': 'apple'}
    ]

    # print(filtering_category(DATABASE, 'Фрукты', 'price_after', True) == test)  # True

    # Проверка работоспособности функций view_in_cart, add_to_cart, remove_from_cart
    # Для совпадения выходных значений перед запуском скрипта удаляйте появляющийся файл 'cart.json' в папке
    print(view_in_cart())  # {'products': {}}
    print(add_to_cart('1'))  # True
    print(add_to_cart('0'))  # False
    print(add_to_cart('1'))  # True
    print(add_to_cart('2'))  # True
    print(view_in_cart())  # {'products': {'1': 2, '2': 1}}
    print(remove_from_cart('0'))  # False
    print(remove_from_cart('1'))  # True
    print(view_in_cart())  # {'products': {'2': 1}}

    # Предыдущий код, что был для проверки filtering_category закомментируйте