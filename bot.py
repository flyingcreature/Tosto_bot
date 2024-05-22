import telebot, logging, os

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
            bot.send_message(user, "Emergency stop activated")
        logging.warning("Emergency stop activated")
        exit(0)


@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для придумывания тостов и поздравлений. Напиши /help для подробностей)",
    )
    io.sing_up(message.from_user.id, message.from_user.first_name)


@bot.message_handler(commands=["help"])
def help(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        "Чтобы сгенерировать тост, напиши /gen\nЧтобы увидить последний сгенерированый тост напиши /last\nОткрыть меню - /menu\n\nP.S. Все эти команды видны в списке слева от поля ввода ;)",
    )


@bot.message_handler(commands=["gen"])
def generate(message: telebot.types.Message): ...


@bot.message_handler(commands=["last"])
def last(message: telebot.types.Message): ...


@bot.message_handler(commands=["menu"])
def menu(message: telebot.types.Message): ...


@bot.message_handler(commands=["logs"])
def logs(message: telebot.types.Message):
    with open(LOGS_PATH, "rb") as file:
        (
            bot.send_document(message.chat.id, file)
            if message.from_user.id in ADMINS
            else None
        )


@bot.message_handler(content_types=["text"])
def text(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        "Кажется я потерял контекст :(\nПожайлуста запусти генерацию или воспользуйся меню.",
    )


bot.infinity_polling(timeout=60, long_polling_timeout=5)
