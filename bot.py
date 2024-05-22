import telebot, logging, os

import db
from config import LOGS_PATH, BOT_TOKEN, ADMINS, DB_TABLE_USERS_CONGRATULATION, DB_TABLE_USERS_NAME
from iop import IOP

io = IOP()

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для придумывания тостов и поздравлений. Напиши /help для подробностей)",
    )
    io.sing_up(message.from_user.id, message.from_user.first_name)

@bot.message_handler(commands=["logs"])
def logs(message: telebot.types.Message):
    with open(LOGS_PATH, "rb") as file:
        (
            bot.send_document(message.chat.id, file)
            if message.from_user.id in ADMINS
            else None
        )

bot.infinity_polling(timeout=60, long_polling_timeout=5)