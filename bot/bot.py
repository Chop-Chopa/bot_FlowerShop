import os

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import bot_handlers

from bot_menu_constants import OCCASIONS


HANDLER_MAP = {
    'choose_occasion': bot_handlers.handle_choose_occasion,
    'ask_occasion': bot_handlers.handle_ask_occasion,
    'choose_flower_color': bot_handlers.handle_choose_flower_color,
    'choose_price': bot_handlers.handle_choose_price,
    'get_user_choice': bot_handlers.handle_get_user_choice,
    'get_user_agreement': bot_handlers.handle_get_user_agreement,
    'ask_name': bot_handlers.handle_ask_name,
    'ask_address': bot_handlers.handle_ask_address,
    'ask_date_time': bot_handlers.handle_ask_date_time,
    'get_user_data_choice': bot_handlers.handle_get_user_data_choice,
    'ask_phone': bot_handlers.handle_ask_phone,
}


def start(update, context):
    """Обработчик команды /start."""
    context.user_data.clear()
    update.message.reply_text(
        'Вас приветствует чат-бот магазина Flower Shop.'
        ' К какому событию готовимся? Выберите один из вариантов, либо укажите свой:',
        reply_markup=bot_handlers.build_keyboard('choose_occasion', OCCASIONS)
    )


def button_handler(update, context):
    """Общий обработчик нажатий кнопок."""
    query = update.callback_query
    query.answer()
    data = query.data.strip()

    if data in HANDLER_MAP:
        action = data
        param = None
    else:
        if '_' in data:
            action, param = data.rsplit('_', 1)
        else:
            action = data
            param = None
    handler = HANDLER_MAP.get(action)
    if handler:
        handler(update, context, param)
    else:
        query.edit_message_text('Выбор не распознан, нажмите /start для начала.')


def message_handler(update, context):
    """Обработчик текстового сообщения."""
    current_step = context.user_data.get('current_step')

    if current_step and current_step in HANDLER_MAP:
        HANDLER_MAP[current_step](update, context)
        return

    else:
        update.message.reply_text("Пожалуйста, выберите действие из меню или нажмите /start.")


def run_bot():
    load_dotenv()
    tg_token = os.environ['TG_TOKEN']

    updater = Updater(tg_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()
