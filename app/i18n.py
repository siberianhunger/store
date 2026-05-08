from flask import redirect, request, session, url_for


SUPPORTED_LOCALES = ("ru", "en")
DEFAULT_LOCALE = "ru"


TRANSLATIONS = {
    "ru": {
        "brand": "Baikal Stone Market",
        "catalog": "Каталог",
        "checkout": "Оформление",
        "track_order": "Отследить заказ",
        "cart": "Корзина",
        "lake_stones": "Камни Байкала",
        "hero_title": "Байкальские камни для тихого интерьера",
        "hero_copy": "Небольшая подборка природных камней с берегов Байкала: спокойные формы, холодные оттенки и фактура для полки, стола или витрины.",
        "stones_available": "камней в подборке",
        "choose_stone": "Выберите камень",
        "all": "Все",
        "no_filter_results": "Нет камней для этого фильтра.",
        "main_navigation": "Основная навигация",
        "language": "Язык",
        "filter_by_color": "Фильтр по оттенку",
        "add": "Добавить",
        "add_to_cart": "Добавить в корзину",
        "weight": "Вес",
        "stock": "Наличие",
        "finish": "Поверхность",
        "color": "Цвет",
        "cart_empty": "Корзина пуста.",
        "qty": "Количество",
        "checkout_button": "Оформить",
        "update": "Обновить",
        "remove": "Удалить",
        "total": "Итого",
        "shipping_details": "Доставка",
        "name": "Имя",
        "email": "Email",
        "phone": "Телефон",
        "shipping_address": "Адрес доставки",
        "place_order": "Оформить заказ",
        "order_summary": "Состав заказа",
        "manual_payment_note": "Онлайн-оплата пока не подключена. Мы свяжемся с вами и согласуем оплату вручную.",
        "order_confirmed": "Заказ принят",
        "order": "Заказ",
        "order_status": "Статус заказа",
        "order_code": "Код заказа",
        "access_key": "Ключ доступа",
        "items": "Позиции",
        "back_to_catalog": "Вернуться в каталог",
        "continue_payment": "Продолжить оплату",
        "payment_status": "Статус оплаты",
        "pending_manual": "Ожидает согласования оплаты",
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
        "validation_stock": "Запрошенное количество сейчас недоступно.",
        "product_not_found": "Товар не найден.",
        "only_available": "Запрошенное количество сейчас недоступно.",
        "quantity_negative": "Количество не может быть отрицательным.",
        "payment_created": "Платеж создан. Продолжите оплату.",
        "payment_pending_copy": "Оплата пока не подтверждена.",
        "payment_paid_copy": "Оплата подтверждена.",
        "manual_pending_copy": "Оплату нужно согласовать вручную.",
        "order_email_copy": "Заказ оформлен на",
        "order_private_copy": "Детали заказа скрыты. Чтобы открыть их, введите код заказа, email и ключ доступа.",
        "track_order_title": "Отследить заказ",
        "track_order_copy": "Введите код заказа, email и ключ доступа, который был показан после оформления.",
        "tracking_error": "Заказ с такими данными не найден.",
        "save_access_key": "Сохраните ключ доступа",
        "save_access_key_copy": "Он понадобится, чтобы позже открыть заказ без аккаунта.",
        "manual_review": "Требует проверки",
        "refunded": "Возвращено",
        "refund_pending": "Возврат в обработке",
        "refund_failed": "Ошибка возврата",
        "shipped": "Отправлен",
        "shipping": "Доставка",
        "shipping_carrier": "Служба доставки",
        "tracking_number": "Трек-номер",
        "tracking_link": "Открыть отслеживание",
        "shipping_note": "Комментарий к доставке",
        "shipped_at": "Дата отправки",
    },
    "en": {
        "brand": "Baikal Stone Market",
        "catalog": "Catalog",
        "checkout": "Checkout",
        "track_order": "Track order",
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
        "order_status": "Order status",
        "order_code": "Order code",
        "access_key": "Access key",
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
        "only_available": "Requested quantity is not available.",
        "quantity_negative": "Quantity cannot be negative.",
        "payment_created": "Payment was created. Continue payment.",
        "payment_pending_copy": "Payment is not confirmed yet.",
        "payment_paid_copy": "Payment is confirmed.",
        "manual_pending_copy": "Payment is pending manual handling.",
        "order_email_copy": "Confirmation has been recorded for",
        "order_private_copy": "Order details are protected. Enter the order code, email, and access key to view them.",
        "track_order_title": "Check an order",
        "track_order_copy": "Enter the order code, email, and access key from the confirmation screen.",
        "tracking_error": "No order was found for those details.",
        "save_access_key": "Save this access key",
        "save_access_key_copy": "You will need it to view this order later without an account.",
        "manual_review": "Needs review",
        "refunded": "Refunded",
        "refund_pending": "Refund pending",
        "refund_failed": "Refund failed",
        "shipped": "Shipped",
        "shipping": "Shipping",
        "shipping_carrier": "Carrier",
        "tracking_number": "Tracking number",
        "tracking_link": "Open tracking",
        "shipping_note": "Shipping note",
        "shipped_at": "Shipped at",
    },
}


COLOR_LABELS = {
    "ru": {
        "brown": "Теплые",
        "dark": "Темные",
        "grey": "Серые",
        "pale": "Светлые",
        "striped": "Полосы",
        "veined": "Прожилки",
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
