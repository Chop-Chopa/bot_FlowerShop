import os
from dotenv import load_dotenv
import telebot
from telebot import types
from telebot.types import Message

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не найден в .env")

bot = telebot.TeleBot(TOKEN)

# Временное хранилище состояний пользователей (в памяти)
user_states = {}
message_history = {} 



# Тестовая "база" букетов
BOUQUETS = [
    {"name": "Scarlet Romance", "occasion": "Свадьба", "color": "Красный", "budget": "~2000",
     "description": "Красивый букет роз — для романтических моментов."},
    {"name": "Pink Dreams", "occasion": "День рождения", "color": "Розовый", "budget": "~1000",
     "description": "Нежный букет в пастельных тонах — подарок для именинника."},
    {"name": "White Elegance", "occasion": "Другой повод", "color": "Белый", "budget": "~2000",
     "description": "Сдержанный букет для офиса и деловых событий."},
    {"name": "Sunny Smile", "occasion": "Без повода", "color": "Жёлтый", "budget": "~500",
     "description": "Яркий, солнечный букет для поднятия настроения."},
    {"name": "Festive Mix", "occasion": "В школу", "color": "Фиолетовые", "budget": "Больше",
     "description": "Праздничный букет с эксклюзивными цветами."},
    {"name": "Pastel Bliss", "occasion": "Свадьба", "color": "На ваш выбор", "budget": "~1000",
     "description": "Лёгкий романтичный букет в пастельных тонах."},
]

# Опции для шагов
STEP1_OPTIONS = ["Свадьба", "В школу", "День рождения", "Без повода", "Другой повод"]  # 5
STEP2_OPTIONS = ["Красный", "Розовый", "Белый", "Жёлтый", "Фиолетовые", "На ваш выбор"]   # 6
STEP3_OPTIONS = ["~500", "~1000", "~2000", "Больше", "Не важно"]                 # 5

def clear_message_history(chat_id):
    """Удаляет все сохраненные сообщения для указанного чата"""
    if chat_id in message_history:
        for message_id in message_history[chat_id]:
            try:
                bot.delete_message(chat_id, message_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        del message_history[chat_id]

# Функция для сохранения ID сообщений
def save_message_id(chat_id, message_id):
    if chat_id not in message_history:
        message_history[chat_id] = []
    message_history[chat_id].append(message_id)

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = {"step": 0, "choice1": None, "choice2": None, "choice3": None, "last_bouquet": None, "file_viewed": False}
    return user_states[user_id]

def build_agreement_buttons():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("Соглашаюсь", callback_data="agree:yes"),
        types.InlineKeyboardButton("Отказаться", callback_data="agree:no")
    )
    return kb

def build_inline_buttons(options, prefix):
    kb = types.InlineKeyboardMarkup()
    buttons = []
    for opt in options:
        btn = types.InlineKeyboardButton(text=opt, callback_data=f"{prefix}:{opt}")
        buttons.append(btn)
    # добавляем кнопки по 2 в ряд
    row = []
    for i, b in enumerate(buttons, start=1):
        row.append(b)
        if i % 2 == 0:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)
    return kb

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    clear_message_history(message.chat.id) 
    state = get_user_state(uid)
    state.update({
        "step": 1, 
        "choice1": None, 
        "choice2": None, 
        "choice3": None, 
        "last_bouquet": None,
        "file_viewed": False
    })
    text = "Привет! Давай подберём букет. Сначала: выбери случай/повод:"
    kb = build_inline_buttons(STEP1_OPTIONS, "step1")
    msg = bot.send_message(message.chat.id, text, reply_markup=kb)
    save_message_id(message.chat.id, msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("step1:"))
def handle_step1(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    choice = call.data.split(":", 1)[1]
    state = get_user_state(uid)
    state["choice1"] = choice
    state["step"] = 2
    # отправляем второй выбор
    text = f"Вы выбрали: {choice}\nТеперь выберите цветовую гамму:"
    kb = build_inline_buttons(STEP2_OPTIONS, "step2")
    bot.send_message(call.message.chat.id, text, reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("step2:"))
def handle_step2(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    choice = call.data.split(":", 1)[1]
    state = get_user_state(uid)
    state["choice2"] = choice
    state["step"] = 3
    # отправляем третий выбор
    text = f"Вы выбрали: {choice}\nИ наконец, выберите бюджет:"
    kb = build_inline_buttons(STEP3_OPTIONS, "step3")
    bot.send_message(call.message.chat.id, text, reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("step3:"))
def handle_step3(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    choice = call.data.split(":", 1)[1]
    state = get_user_state(uid)
    state["choice3"] = choice
    state["step"] = 0
    # Подбор букета
    bouquet = find_best_bouquet(state["choice1"], state["choice2"], state["choice3"])
    state["last_bouquet"] = bouquet
    if bouquet:
        text = (f"Подходящий букет: {bouquet['name']}\n"
                f"Описание: {bouquet['description']}\n"
                f"Подбор по: {state['choice1']} / {state['choice2']} / {state['choice3']}")
    else:
        text = ("К сожалению, точного совпадения не найдено. Попробуйте выбрать другие параметры.\n"
                f"Ваши параметры: {state['choice1']} / {state['choice2']} / {state['choice3']}")
    # Кнопки действий: Сделать заказ, другой букет, Заказать консультацию флориста
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("Сделать заказ", callback_data="action:order"),
        types.InlineKeyboardButton("Другой букет", callback_data="action:another")
    )
    kb.row(types.InlineKeyboardButton("Заказать консультацию флориста", callback_data="action:consult"))
    bot.send_message(call.message.chat.id, text, reply_markup=kb)

def find_best_bouquet(occa, color, budget):
    # Попробуем точное совпадение
    matches = [b for b in BOUQUETS if b["occasion"] == occa and b["color"] == color and b["budget"] == budget_name_map(budget)]
    if matches:
        return matches[0]
    # Попробуем частичное совпадение: 2 признака
    scored = []
    for b in BOUQUETS:
        score = 0
        if b["occasion"] == occa:
            score += 1
        if b["color"] == color:
            score += 1
        if b["budget"] == budget_name_map(budget):
            score += 1
        scored.append((score, b))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored and scored[0][0] > 0:
        return scored[0][1]
    return None

def budget_name_map(user_budget):
    return user_budget

@bot.callback_query_handler(func=lambda call: call.data.startswith("action:"))
def handle_action(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    action = call.data.split(":", 1)[1]
    state = get_user_state(uid)
    
    if action in ["order", "consult"]:
        file_path = os.path.join(os.getcwd(), 'documents', 'pd.pdf')
        try:
            with open('pd.pdf', 'rb') as file:
                bot.send_document(call.message.chat.id, file, caption="Ознакомьтесь с условиями")
                bot.send_message(
                    call.message.chat.id,
                    "Пожалуйста, ознакомьтесь с документом и выберите действие:",
                    reply_markup=build_agreement_buttons()
                )
        except FileNotFoundError:
            bot.send_message(call.message.chat.id, "Файл с условиями не найден. Попробуйте позже.")
        return
    
    if action == "order":
        bouquet = state.get("last_bouquet")
        if bouquet:
            bot.send_message(
                call.message.chat.id,
                f"Отлично! Вы выбрали '{bouquet['name']}'.\n"
                "Для оформления заказа оставьте, пожалуйста, свой контакт (телефон или email)."
            )
            state["step"] = "awaiting_contact"
        else:
            bot.send_message(call.message.chat.id, "Букет не выбран — сначала выберите букет.")
    
    elif action == "consult":
        bot.send_message(
            call.message.chat.id,
            "Свяжемся с флористом для консультации. Пожалуйста, оставьте контакт (телефон или email)."
        )
        state["step"] = "awaiting_contact"
    
    elif action == "another":
        state.update({
            "step": 1, 
            "choice1": None, 
            "choice2": None, 
            "choice3": None, 
            "last_bouquet": None
        })
        kb = build_inline_buttons(STEP1_OPTIONS, "step1")
        bot.send_message(
            call.message.chat.id,
            "Хорошо, начнём заново. Выберите случай/повод:",
            reply_markup=kb
        )
    
    else:
        bot.send_message(call.message.chat.id, "Неизвестное действие.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("agree:"))
def handle_agreement(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    choice = call.data.split(":", 1)[1]
    state = get_user_state(uid)
    
    if choice == "yes":
        bot.send_message(
            call.message.chat.id,
            "Спасибо за согласие! Теперь оставьте, пожалуйста, свой контакт (телефон или email)."
        )
        state["step"] = "awaiting_contact"

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    state = get_user_state(uid)
    
    if state.get("step") == "awaiting_contact":
        contact = message.text.strip()
        bot.send_message(message.chat.id, f"Спасибо! Мы получили контакт: {contact}\nС вами свяжутся в ближайшее время.")
        state["step"] = 0
    
    # Добавляем обработку просмотра файла
    elif state.get("file_path"):
        state["file_viewed"] = True
        bot.send_message(message.chat.id, "Вы ознакомились с информацией. Хотите оформить заказ или заказать флориста?")
        
        kb = types.InlineKeyboardMarkup()
        btn_order = types.InlineKeyboardButton("Оформить заказ", callback_data="action:order")
        btn_florist = types.InlineKeyboardButton("Заказать флориста", callback_data="action:florist")
        kb.row(btn_order, btn_florist)
        
        bot.send_message(message.chat.id, "", reply_markdown=kb)
    
    else:
        bot.send_message(message.chat.id, "Чтобы начать подбор букета, используйте /start")

# Добавляем новый обработчик для отправки файла
@bot.callback_query_handler(func=lambda call: call.data.startswith("show_file"))
def send_file(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    state = get_user_state(uid)
    
    try:
        # Отправляем файл пользователю
        with open('file.pdf', 'rb') as file:
            bot.send_document(call.message.chat.id, file, caption="Ознакомьтесь с информацией")
            state["file_path"] = 'file.pdf'
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, "Файл не найден. Попробуйте позже.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Произошла ошибка при отправке файла: {str(e)}")
    finally:
        # Здесь можно добавить код, который должен выполниться в любом случае
        pass

if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()
