import telebot, logging, os, time

import db
from config import (
    LOGS_PATH,
    BOT_TOKEN,
    ADMINS,
    DB_TABLE_USERS_CONGRATULATION,
    DB_TABLE_USERS_NAME,
)
from iop import IOP

io = IOP()

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
    bot.send_message(
        message.chat.id,
        "Ок давай сгенерируем тост. Отправь имя человека и на какой праздник генерируем поздравление через пробел",
    )
    bot.register_next_step_handler(message, name_event)


def name_event(message: telebot.types.Message):
    if len(message.text.split(",")) == 2:
        name, event = tuple(message.text.split(","))
    else:
        bot.send_message(message.chat.id, "Извини, но вы не правильно составили запрос, попробуйте еще раз. Не забудьте про запятую).")
        name, event = None, None
        bot.register_next_step_handler(message, name_event)

    if name and event:
        today = time.time()
        bot.send_chat_action(message.chat.id, "typing")
        io.updd_pgen(message.from_user.id, event, name, today)
        result = io.generate(message.from_user.id)
        bot.send_message(message.chat.id, result)
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(
            message.chat.id,
            "Не за что",
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
        bot.send_message(
            message.chat.id,
            "Меню:",
            reply_markup=io.get_inline_keyboard(
                (("Указать свою дату", "myb"), ("Выбрать длинну поздравлений", "lent"))))


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
