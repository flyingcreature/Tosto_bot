import telebot, logging, time, random, json

import db
from config import *
from iop import IOP, Monetize

io = IOP()
mt = Monetize()

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["emergency_stop"])
def emergency_stop(message: telebot.types.Message):
    if message.from_user.id in ADMINS:
        for user in ADMINS:
            bot.send_chat_action(user, "typing")
            bot.send_message(user, "Emergency stop activated")
        logging.warning("Emergency stop activated")
        exit(0)


@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для придумывания тостов и поздравлений. Напиши /help для подробностей или залетай в /menu)",
    )
    io.sing_up(message.from_user.id, message.from_user.first_name)


@bot.message_handler(commands=["help"])
def help(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id,
        "Чтобы сгенерировать тост, напиши /gen\nЧтобы увидить последний сгенерированый тост напиши /last\nОткрыть меню - /menu\n\nP.S. Все эти команды видны в списке слева от поля ввода ;)\nP.S.#2 В контексте бота тост == поздравление",
    )


@bot.message_handler(commands=["gen"])
def generate(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, "typing")

    if db.get_user_data(message.from_user.id)["gpt_tokens"] >= MAX_USER_GPT_TOKENS:
        bot.send_message(
            message.chat.id,
            "У вас недостаточно токенов для генерации тоста. Получить токены можно в меню, а пока лови рандомное поздравление",
        )
        bot.send_chat_action(message.chat.id, "typing")
        with open("offline.json", "r") as f:
            offline_toasts = json.load(f)                    
            bot.send_message(message.chat.id, random.choice(offline_toasts))
            return
        
    bot.send_message(
        message.chat.id,
        "Ок давай сгенерируем тост. Отправь имя человека",
    )
    bot.register_next_step_handler(message, name_name)

def name_name(message: telebot.types.Message):
    io.updd_pgen(message.from_user.id, None, message.text, time.time())
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(message.chat.id, "Теперь отправь название мероприятия")
    bot.register_next_step_handler(message, event_event)

def event_event(message: telebot.types.Message):
    io.updd_pgen(message.from_user.id, message.text, None, time.time())
    bot.send_chat_action(message.chat.id, "typing")
    if not db.get_user_data(message.from_user.id)["long_congratulation"]:
        bot.send_message(message.chat.id, "Теперь отправь длинну поздравления в предложениях")
        bot.register_next_step_handler(message, long_long)
    else:
        name_event(message)

def long_long(message: telebot.types.Message):
    if message.text.isdigit():
        db.update_row(DB_TABLE_USERS_NAME, message.from_user.id,"long_congratulation", int(message.text))
        name_event(message)

def name_event(message: telebot.types.Message):
        today = time.time()
        bot.send_chat_action(message.chat.id, "typing")
        result = io.generate(message.from_user.id)

        if result == "cd_error":
            bot.send_message(message.chat.id, "Произошла ошибка при генерации тоста(. Лови утешительный тост")
            bot.send_chat_action(message.chat.id, "typing")
            with open("offline.json", "r") as f:
                offline_toasts = json.load(f)                    
            bot.send_message(message.chat.id, random.choice(offline_toasts))

        bot.send_message(message.chat.id, result)
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(
            message.chat.id,
            "Не за что" if result != "cd_error" else "i`m sorry :(",
            reply_markup=telebot.util.quick_markup({"Меню": {"callback_data": "menu"}}),
        )


@bot.message_handler(commands=["last"])
def last(message: telebot.types.Message):
    txt, date = io.last_gen(message.from_user.id)
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(message.chat.id, f"Вот твоя последняя генерация:\n{txt}",
                     reply_markup=telebot.util.quick_markup({"Меню": {"callback_data": "menu"}}))


@bot.callback_query_handler(func=lambda call: call.data == "menu")
@bot.message_handler(commands=["menu"])
def menu(call):
    message: telebot.types.Message = (
        call.message
        if hasattr(call, "message")
        else call.message if isinstance(call, telebot.types.CallbackQuery) else call
    )

    if message is not None:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(
            message.chat.id,
            "Меню:",
            reply_markup=io.get_inline_keyboard(
                (("Указать свое др", "myb"), ("Выбрать длинну поздравлений", "lent"))))

@bot.callback_query_handler(func=lambda call: call.data == "lent")
def lent(call):
    message: telebot.types.Message = (
        call.message if call.message else call.callback_query.message
    )
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(message.chat.id, "Напиши длину поздравлений в предложениях (Только цифра)")
    bot.register_next_step_handler(message, lent_event)

def lent_event(message: telebot.types.Message):
    if message.text.isdigit():
        bot.send_chat_action(message.chat.id, "typing")
        db.update_row(DB_TABLE_USERS_NAME, message.from_user.id,"long_congratulation", int(message.text))
        bot.send_message(message.chat.id, f"Теперь длина поздравлений будет равна {message.text} предложений")
    else:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "Неправильный ввод, попробуй еще раз")
        bot.register_next_step_handler(message, lent_event)

@bot.callback_query_handler(func=lambda call: call.data == "debt")
def get_debt(call):
    message: telebot.types.Message = (
        call.message if call.message else call.callback_query.message
    )
    bot.delete_message(message.chat.id, message.message_id)
    id = message.chat.id
    gpt = round(mt.cost_calculation(id, 'gpt'), 2)
    bot.send_message(id,
                     f"Вот твой счет:\n\n"
                     f"За использование YaGPT: {gpt}₽", parse_mode="Markdown")
    menu(message)

@bot.message_handler(commands=["logs"])
def send_logs(message):
    user_id = message.from_user.id
    if user_id in ADMINS:
        try:
            with open(LOGS_PATH, "rb") as f:
                bot.send_document(message.chat.id, f)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(chat_id=message.chat.id, text="Логов нет!")
    else:
        print(f"{user_id} захотел посмотреть логи")
        logging.info(f"{user_id} захотел посмотреть логи")


@bot.message_handler(content_types=["text"])
def text(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id,
        "Кажется я потерял контекст :(\nПожайлуста запусти генерацию или воспользуйся меню.",
    )


bot.infinity_polling(timeout=60, long_polling_timeout=5)
