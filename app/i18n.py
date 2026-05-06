from flask import redirect, request, session, url_for


SUPPORTED_LOCALES = ("ru", "en")
DEFAULT_LOCALE = "ru"


TRANSLATIONS = {
    "ru": {
        "brand": "Baikal Stone Market",
        "catalog": "Каталог",
        "checkout": "Оформление",
        "cart": "Корзина",
        "lake_stones": "Камни Байкала",
        "hero_title": "Природные камни для спокойного интерьера",
        "hero_copy": "Небольшой каталог сфотографированных камней из байкальского региона, выбранных за цвет, форму и декоративность.",
        "stones_available": "камней в наличии",
        "choose_stone": "Выберите свой камень",
        "all": "Все",
        "no_filter_results": "Нет камней для этого фильтра.",
        "main_navigation": "Основная навигация",
        "language": "Язык",
        "filter_by_color": "Фильтр по цвету",
        "add": "Добавить",
        "add_to_cart": "Добавить в корзину",
        "weight": "Вес",
        "stock": "В наличии",
        "finish": "Поверхность",
        "color": "Цвет",
        "cart_empty": "Корзина пуста.",
        "qty": "Кол-во",
        "checkout_button": "Оформить",
        "update": "Обновить",
        "remove": "Удалить",
        "total": "Итого",
        "shipping_details": "Данные доставки",
        "name": "Имя",
        "email": "Email",
        "phone": "Телефон",
        "shipping_address": "Адрес доставки",
        "place_order": "Оформить заказ",
        "order_summary": "Состав заказа",
        "manual_payment_note": "Онлайн-оплата пока не подключена. Заказ будет обработан вручную.",
        "order_confirmed": "Заказ оформлен",
        "order": "Заказ",
        "items": "Позиции",
        "back_to_catalog": "Вернуться в каталог",
        "continue_payment": "Продолжить оплату",
        "payment_status": "Статус оплаты",
        "pending_manual": "Ожидает ручной оплаты",
        "pending": "Ожидает оплаты",
        "succeeded": "Оплачено",
        "canceled": "Оплата отменена",
        "error": "Ошибка оплаты",
        "awaiting_payment": "Ожидает оплаты",
        "paid": "Оплачено",
        "payment_failed": "Оплата не прошла",
        "payment_error": "Ошибка создания платежа",
        "new": "Новый",
        "validation_cart_empty": "Корзина пуста.",
        "validation_name_required": "Введите имя.",
        "validation_email": "Введите корректный email.",
        "validation_address_required": "Введите адрес доставки.",
        "validation_stock": "Одна или несколько позиций превышают остаток.",
        "product_not_found": "Товар не найден.",
        "only_available": "В наличии только {stock}.",
        "quantity_negative": "Количество не может быть отрицательным.",
        "payment_created": "Платеж создан. Продолжите оплату.",
        "payment_pending_copy": "Оплата еще не подтверждена.",
        "manual_pending_copy": "Оплата ожидает ручной обработки.",
        "order_email_copy": "Заказ записан для",
    },
    "en": {
        "brand": "Baikal Stone Market",
        "catalog": "Catalog",
        "checkout": "Checkout",
        "cart": "Cart",
        "lake_stones": "Lake Baikal stones",
        "hero_title": "Natural stones for quiet interiors",
        "hero_copy": "A small catalog of photographed stones from the Baikal region, selected for color, shape, and decorative presence.",
        "stones_available": "stones available now",
        "choose_stone": "Choose your stone",
        "all": "All",
        "no_filter_results": "No stones match this filter.",
        "main_navigation": "Main navigation",
        "language": "Language",
        "filter_by_color": "Filter by color family",
        "add": "Add",
        "add_to_cart": "Add to cart",
        "weight": "Weight",
        "stock": "Stock",
        "finish": "Finish",
        "color": "Color",
        "cart_empty": "Your cart is empty.",
        "qty": "Qty",
        "checkout_button": "Checkout",
        "update": "Update",
        "remove": "Remove",
        "total": "Total",
        "shipping_details": "Shipping details",
        "name": "Name",
        "email": "Email",
        "phone": "Phone",
        "shipping_address": "Shipping address",
        "place_order": "Place order",
        "order_summary": "Order summary",
        "manual_payment_note": "Online acquiring is not connected yet. This order will be handled manually.",
        "order_confirmed": "Order confirmed",
        "order": "Order",
        "items": "Items",
        "back_to_catalog": "Back to catalog",
        "continue_payment": "Continue payment",
        "payment_status": "Payment status",
        "pending_manual": "Pending manual payment",
        "pending": "Payment pending",
        "succeeded": "Paid",
        "canceled": "Payment canceled",
        "error": "Payment error",
        "awaiting_payment": "Awaiting payment",
        "paid": "Paid",
        "payment_failed": "Payment failed",
        "payment_error": "Payment creation error",
        "new": "New",
        "validation_cart_empty": "Your cart is empty.",
        "validation_name_required": "Name is required.",
        "validation_email": "Enter a valid email.",
        "validation_address_required": "Shipping address is required.",
        "validation_stock": "One or more items exceed available stock.",
        "product_not_found": "Product not found.",
        "only_available": "Only {stock} available.",
        "quantity_negative": "Quantity cannot be negative.",
        "payment_created": "Payment was created. Continue payment.",
        "payment_pending_copy": "Payment is not confirmed yet.",
        "manual_pending_copy": "Payment is pending manual handling.",
        "order_email_copy": "Confirmation has been recorded for",
    },
}


COLOR_LABELS = {
    "ru": {
        "brown": "Коричневые",
        "dark": "Темные",
        "grey": "Серые",
        "pale": "Светлые",
        "striped": "Полосатые",
        "veined": "С прожилками",
    },
    "en": {},
}


def get_locale():
    saved = session.get("locale")
    if saved in SUPPORTED_LOCALES:
        return saved
    match = request.accept_languages.best_match(SUPPORTED_LOCALES)
    return match or DEFAULT_LOCALE


def set_locale(locale):
    if locale in SUPPORTED_LOCALES:
        session["locale"] = locale


def t(key):
    locale = get_locale()
    return TRANSLATIONS.get(locale, TRANSLATIONS[DEFAULT_LOCALE]).get(
        key, TRANSLATIONS[DEFAULT_LOCALE].get(key, key)
    )


def tf(key, **kwargs):
    return t(key).format(**kwargs)


def color_label(color):
    locale = get_locale()
    return COLOR_LABELS.get(locale, {}).get(color, color.title())


def localized_product_name(product):
    locale = get_locale()
    return product[f"name_{locale}"] or product["name"]


def localized_product_description(product):
    locale = get_locale()
    return product[f"description_{locale}"] or product["description"]


def switch_locale_response(locale):
    set_locale(locale)
    target = request.referrer or url_for("store.index")
    return redirect(target)
