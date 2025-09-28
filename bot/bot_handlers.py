import os
import random

from dotenv import load_dotenv
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot_menu_constants import (
    OCCASIONS, FLOWER_COLORS, PRICES,
    USER_CHOICES, USER_AGREEMENT, USER_DATA
)
from find_flower_func import find_flower
from admin_flowershop.models import Product


load_dotenv()


def build_keyboard(action_type, button_rows):
    """Создает клавиатуру, принимает тип действия (для callback_data) и список списков с названиями кнопок."""
    keyboard = [
        [InlineKeyboardButton(text=button_label, callback_data=f"{action_type}_{row_index}")]
        for row_index, [button_label] in enumerate(button_rows)
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_choose_occasion(update, context, param=None):
    """Обработчик кнопок стартового меню."""
    query = update.callback_query
    query.answer()

    if param == '4':
        context.user_data['current_step'] = 'ask_occasion'
        query.edit_message_text(
            text="Пожалуйста, уточните повод для букета:"
        )
        context.user_data['occasion'] = 'Без повода'
    else:
        context.user_data['occasion'] = OCCASIONS[int(param)][0]
        query.edit_message_text(
            text="Какой оттенок букета Вы предпочитаете?",
            reply_markup = build_keyboard('choose_flower_color', FLOWER_COLORS)
        )


def handle_ask_occasion(update, context, param=None):
    update.message.reply_text(
        text="Какой оттенок букета Вы предпочитаете?",
        reply_markup = build_keyboard('choose_flower_color', FLOWER_COLORS)
    )


def handle_choose_flower_color(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param != '5':
        context.user_data['flower_color'] = FLOWER_COLORS[int(param)][0]

    query.edit_message_text(
        text="На какую сумму рассчитываете?",
        reply_markup=build_keyboard('choose_price', PRICES)
    )


def handle_choose_price(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param != '4':
        context.user_data['price'] = PRICES[int(param)][0]

    bouquet = find_flower(context.user_data)

    if bouquet is None:
        qs_random = Product.objects.filter(available=True).prefetch_related(
            'color_themes', 'categories'
        ).only('id', 'name', 'price', 'image', 'description', 'composition')
        total = qs_random.count()

        bouquet = qs_random[random.randrange(total)]
        prefix = "Извините, мы не нашли букет по вашим запросам.\n"
    else:
        prefix = ""

    color_names = ", ".join(ct.name for ct in bouquet.color_themes.all()) or "—"

    caption = (
        prefix +
        f"Мы предлагаем вам букет {bouquet.name}!\n"
        f"Описание: {bouquet.description};\n"
        f"Цветовая палитра: {color_names};\n"
        f"Цена: {bouquet.price};\n"
        f"Цветочный состав: {bouquet.composition};\n"
        "Хотите что-то еще более уникальное? Подберите другой букет из нашей коллекции "
        "или закажите консультацию флориста."
    )

    chat_id = query.message.chat.id

    with open(bouquet.image.path, "rb") as photo:
        context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_markup=build_keyboard('get_user_choice', USER_CHOICES)
        )


def handle_get_user_choice(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param == '0':
        context.user_data.clear()
        chat_id = query.message.chat.id
        message_id = query.message.message_id

        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

        context.bot.send_message(
            chat_id=chat_id,
            text=('Вас приветствует чат-бот магазина Flower Shop.\n'
                  'К какому событию готовимся? Выберите один из вариантов, либо укажите свой:'),
            reply_markup=build_keyboard('choose_occasion', OCCASIONS)
        )
    elif param == '1':
        policy_url = os.getenv("POLICY_URL", "Ссылка недоступна, свяжитесь с нами, мы предоставим!")
        chat_id = query.message.chat.id
        message_id = query.message.message_id

        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

        context.bot.send_message(
            chat_id=chat_id,
            text='Для того, чтобы продолжить вам необходимо принять пользовательское соглашение'
                 ' и ознакомиться с политикой обработки'
                 f' персональных данных: {policy_url}',
            reply_markup=build_keyboard('get_user_agreement', USER_AGREEMENT)
        )
    elif param == '2':
        qs_random = Product.objects.filter(available=True).prefetch_related(
            'color_themes', 'categories'
        ).only('id', 'name', 'price', 'image', 'description', 'composition')
        total = qs_random.count()

        bouquet = qs_random[random.randrange(total)]

        color_names = ", ".join(ct.name for ct in bouquet.color_themes.all()) or "—"

        caption = (
            f"Мы предлагаем вам букет {bouquet.name}!\n"
            f"Описание: {bouquet.description};\n"
            f"Цветовая палитра: {color_names};\n"
            f"Цена: {bouquet.price};\n"
            f"Цветочный состав: {bouquet.composition};\n"
            "Хотите что-то еще более уникальное? Подберите другой букет из нашей коллекции "
            "или закажите консультацию флориста."
        )
        chat_id = query.message.chat.id

        with open(bouquet.image.path, "rb") as photo:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=build_keyboard('get_user_choice', USER_CHOICES)
            )
    else:
        context.user_data['current_step'] = 'florist'
        policy_url = os.getenv("POLICY_URL", "Ссылка недоступна, свяжитесь с нами, мы предоставим!")
        chat_id = query.message.chat.id
        message_id = query.message.message_id

        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

        context.bot.send_message(
            chat_id=chat_id,
            text='Для того, чтобы продолжить вам необходимо принять пользовательское соглашение'
                 ' и ознакомиться с политикой обработки'
                 f' персональных данных: {policy_url}',
            reply_markup=build_keyboard('get_user_agreement', USER_AGREEMENT)
        )


def handle_get_user_agreement(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param == '0' and context.user_data.get('current_step') == 'florist':
        context.user_data['current_step'] = 'ask_phone'
        query.edit_message_text(
            text='Напишите пожалуйста свой номер телефона, наш флорист свяжется с вами:'
        )
    elif param == '0':
        context.user_data['current_step'] = 'ask_name'
        query.edit_message_text(
            text='Напишите пожалуйста свое имя:'
        )
    else:
        context.user_data.clear()
        chat_id = query.message.chat.id
        message_id = query.message.message_id

        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

        context.bot.send_message(
            chat_id=chat_id,
            text=('Вас приветствует чат-бот магазина Flower Shop.\n'
                  'К какому событию готовимся? Выберите один из вариантов, либо укажите свой:'),
            reply_markup=build_keyboard('choose_occasion', OCCASIONS)
        )


def handle_ask_phone(update, context, param=None):
    user_data = context.user_data
    user_phone = update.message.text.strip()

    user_data['phone'] = user_phone
    user_data['current_step'] = 'choose_price'

    if user_data['occasion'] == 'Без повода':
        occasion_for_florist = 'Уточнить повод'
    else:
        occasion_for_florist = user_data['occasion']

    if user_data.get('price'):
        price_for_florist = user_data['price']
    else:
        price_for_florist = 'Уточнить цену'

    florist_text = (
        f"Новая заявка!\n"
        f"Телефон: {user_data.get('phone')};\n"
        f"Повод: {occasion_for_florist};\n"
        f"Цена: {price_for_florist}.\n"
    )

    florist_chat_id = os.environ["FLORIST_CHAT_ID"]

    context.bot.send_message(chat_id=florist_chat_id, text=florist_text)

    bouquet = find_flower(context.user_data)

    if bouquet is None:
        qs_random = Product.objects.filter(available=True).prefetch_related(
            'color_themes', 'categories'
        ).only('id', 'name', 'price', 'image', 'description', 'composition')
        total = qs_random.count()

        bouquet = qs_random[random.randrange(total)]

    color_names = ", ".join(ct.name for ct in bouquet.color_themes.all()) or "—"

    caption = (
        f"А пока вы ждете, можете посмотреть вариант из готовой коллекции:\n\n"
        f"Мы предлагаем вам букет {bouquet.name}!\n"
        f"Описание: {bouquet.description};\n"
        f"Цветовая палитра: {color_names};\n"
        f"Цена: {bouquet.price};\n"
        f"Цветочный состав: {bouquet.composition};\n"
        "Хотите что-то еще более уникальное? Подберите другой букет из нашей коллекции "
        "или закажите консультацию флориста."
    )

    chat_id = update.message.chat.id

    with open(bouquet.image.path, "rb") as photo:
        context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_markup=build_keyboard('get_user_choice', USER_CHOICES)
        )


def handle_ask_name(update, context, param=None):
    user_data = context.user_data
    user_name = update.message.text.strip()

    user_data['name'] = user_name
    user_data['current_step'] = 'ask_address'

    update.message.reply_text(
        f"Спасибо, {user_name}! 🌸\n\nПожалуйста, введите ваш адрес:"
    )


def handle_ask_address(update, context, param=None):
    user_data = context.user_data
    user_address = update.message.text.strip()

    user_data['address'] = user_address
    user_data['current_step'] = 'ask_date_time'

    update.message.reply_text(
        f"Укажите пожалуйста дату и время доставки:"
    )


def handle_ask_date_time(update, context, param=None):
    user_data = context.user_data
    user_date_time = update.message.text.strip()

    user_data['date_time'] = user_date_time
    user_data['current_step'] = 'get_user_data_choice'

    confirmation_message = (
        f"Вот ваши данные:\n"
        f"Имя: {user_data['name']};\n"
        f"Адрес: {user_data['address']};\n"
        f"Дата и время доставки: {user_date_time}.\n"
    )

    update.message.reply_text(
        confirmation_message,
        reply_markup=build_keyboard('get_user_data_choice', USER_DATA)
    )


def handle_get_user_data_choice(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param == '0':
        context.user_data['current_step'] = 'ask_name'
        query.edit_message_text(
            text='Напишите пожалуйста свое имя:'
        )
    elif param == '1':
        context.user_data.clear()
        chat_id = query.message.chat.id
        message_id = query.message.message_id

        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

        context.bot.send_message(
            chat_id=chat_id,
            text=('Вас приветствует чат-бот магазина Flower Shop.\n'
                  'К какому событию готовимся? Выберите один из вариантов, либо укажите свой:'),
            reply_markup=build_keyboard('choose_occasion', OCCASIONS)
        )
    else:
        courier_chat_id = os.environ['COURIER_CHAT_ID']
        courier_text = (
            f"Новый заказ!\n"
            f"Клиент: {context.user_data['name']};\n"
            f"Адрес: {context.user_data['address']};\n"
            f"Время: {context.user_data['date_time']}.\n"
        )

        context.bot.send_message(chat_id=courier_chat_id, text=courier_text)

        query.edit_message_text(
            text=f"Уважаемый {context.user_data['name']}"
                f" Ваш заказ успешно сформирован, ожидайте доставку"
                f" {context.user_data['date_time']}"
                f" по адресу {context.user_data['address']}.\n\n"
                f"Пожалуйста, выберите действие из меню или нажмите /start."
        )