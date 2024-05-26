import telebot, logging, time, random, json

import db
from config import (
    LOGS_PATH,
    BOT_TOKEN,
    ADMINS,
    MAX_USER_GPT_TOKENS,
    DB_TABLE_USERS_NAME,
)
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
    io.delete_reply_markup(bot, message)
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id,
        "Привет👋🏿! Я бот для придумывания тостов и поздравлений📝."
        "\n\nНапишите /help для подробностей или давайте сразу, что-нибудь придумаем /gen 💥",
    )
    io.sing_up(message.from_user.id, message.from_user.first_name)


@bot.message_handler(commands=["help"])
def send_help(message: telebot.types.Message):
    io.delete_reply_markup(bot, message)
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id,
        "Чтобы сгенерировать тост, напиши /gen 🖊️\n\n Чтобы увидить последний сгенерированый тост напишите /last 📃"
        "\n\nОткрыть меню - /menu 📲\n\n👈P.S. Все эти команды видны в списке слева от поля ввода."
        "\nP.S.#2 В контексте бота тост == поздравление 🎉",
    )


@bot.message_handler(commands=["gen"])
def generate(message: telebot.types.Message):
    io.delete_reply_markup(bot, message)
    bot.send_chat_action(message.chat.id, "typing")

    if (
            db.get_user_data(DB_TABLE_USERS_NAME, message.from_user.id)["gpt_tokens"]
            >= MAX_USER_GPT_TOKENS
    ):
        bot.send_message(
            message.chat.id,
            "У вас недостаточно токенов для генерации тоста 🙁\n"
            "Получить токены можно в меню, а пока лови рандомное поздравление 😊",
        )
        bot.send_chat_action(message.chat.id, "typing")
        with open("offline.json", "r", encoding="utf-8") as f:
            offline_toasts = json.load(f)
            bot.send_message(message.chat.id, random.choice(offline_toasts))
            return

    bot.send_message(
        message.chat.id,
        "Давайте вместе придумаем тост! Напишите кого мы будем поздравлять 🥳?(Можно имя))",
    )
    bot.register_next_step_handler(message, name_name)


def name_name(message: telebot.types.Message):
    io.updd_pgen(message.from_user.id, None, message.text, time.time())
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id, "Так же укажите на какое мероприятие будем писать тост 🎭"
    )
    bot.register_next_step_handler(message, event_event)


def event_event(message: telebot.types.Message):
    io.updd_pgen(message.from_user.id, message.text, None, time.time())
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id, "Теперь отправьте длину поздравления в предложениях 📏"
    )
    bot.register_next_step_handler(message, long_long)


def long_long(message: telebot.types.Message):
    if message.text.isdigit():
        db.update_row(
            DB_TABLE_USERS_NAME,
            message.from_user.id,
            "long_congratulation",
            int(message.text),
        )
        name_event(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста напишите цифрами (1,2,3 ...)")
        bot.register_next_step_handler(message, long_long)


def name_event(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, "typing")
    result = io.generate(message.from_user.id, message.from_user.first_name)

    if result == "cd_error":
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при генерации тоста 🙁\nЛови утешительный тост 😊:",
        )
        bot.send_chat_action(message.chat.id, "typing")
        with open("offline.json", "r", encoding="utf-8") as f:
            offline_toasts = json.load(f)
        bot.send_message(message.chat.id, random.choice(offline_toasts))

    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=["last"])
def last(message: telebot.types.Message):
    io.delete_reply_markup(bot, message)
    txt = db.select_n_last_messages(message.chat.id)
    if db.get_user_data(DB_TABLE_USERS_NAME, message.from_user.id)["code_last"]:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(
            message.chat.id,
            f"Вот ваши последние генерации ✉️:\n\n```json\n{txt}```",
            reply_markup=telebot.util.quick_markup({"Меню": {"callback_data": "menu"}}),
            parse_mode="markdown",
        )
    else:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "Вот ваши последние генерации ✉️:")
        for gen in txt:
            bot.send_chat_action(message.chat.id, "typing")
            bot.send_message(message.chat.id, gen[0])


@bot.callback_query_handler(func=lambda call: call.data == "menu")
@bot.message_handler(commands=["menu"])
def menu(call):
    message: telebot.types.Message = (
        call.message
        if hasattr(call, "message")
        else call.message if isinstance(call, telebot.types.CallbackQuery) else call
    )

    if message is not None:
        io.delete_reply_markup(bot, message, False)
        io.delete_reply_markup(bot, message)
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(
            message.chat.id,
            "Меню:",
            reply_markup=io.get_inline_keyboard(
                (
                    ("Указать свой день рождения (в разработке)", "myb"),
                    ("Изменить вид отображения последних генераций", "ch_code_last"),
                    ("Показать счет", "debt"),
                )
            ),
        )


@bot.callback_query_handler(func=lambda call: call.data == "debt")
def get_debt(call):
    message: telebot.types.Message = (
        call.message if call.message else call.callback_query.message
    )
    bot.delete_message(message.chat.id, message.message_id)
    gpt = round(mt.cost_calculation(message.chat.id, "gpt"), 2)
    bot.send_message(
        message.chat.id,
        f"Вот ваш счет 💰:\n\n" f"За использование YaGPT: {gpt}₽",
        reply_markup=telebot.util.quick_markup({"Меню": {"callback_data": "menu"}}),
    )


@bot.callback_query_handler(func=lambda call: call.data == "ch_code_last")
def ch_last(call):
    message: telebot.types.Message = (
        call.message if call.message else call.callback_query.message
    )
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(
        message.chat.id,
        f"Выберите из списка вариант отображения 🙂",
        reply_markup=io.get_reply_markup(["code", "обычный"]),
    )
    bot.register_next_step_handler(message, sl_last)


def sl_last(message: telebot.types.Message):
    if message.text == "code":
        db.update_row(DB_TABLE_USERS_NAME, message.from_user.id, "code_last", True)
        bot.send_message(
            message.chat.id,
            "Выбран вариант отображения последних генераций в виде кода 👨‍💻",
            reply_markup=telebot.types.ReplyKeyboardRemove(),
        )
    elif message.text == "обычный":
        db.update_row(DB_TABLE_USERS_NAME, message.from_user.id, "code_last", False)
        bot.send_message(
            message.chat.id,
            "Выбран вариант отображения последних генераций в виде текста 💬",
            reply_markup=telebot.types.ReplyKeyboardRemove(),
        )
    else:
        bot.send_message(
            message.chat.id,
            "Пожалуйста выберите вариант из списка [code👨‍💻/обычный💬]",
            reply_markup=io.get_reply_markup(["code", "обычный"]),
        )
        bot.register_next_step_handler(message, sl_last)


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


@bot.message_handler(commands=["kill_my_session"])
def kill_session(message: telebot.types.Message):
    user_id = message.from_user.id
    if user_id in ADMINS:
        try:
            db.update_row(DB_TABLE_USERS_NAME, user_id, "gpt_tokens", 0)
        except Exception as e:
            print(f"Произошла ошибка {e}, сессии не обновлены")
            logging.error(f"Произошла ошибка {e}, сессии не обновлены")
    else:
        print(f"{user_id} попытался обновить сессии")
        logging.info(f"{user_id} попытался обновить сессии")


@bot.message_handler(content_types=["text"])
def text(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, "typing")
    io.delete_reply_markup(bot, message)
    bot.send_message(
        message.chat.id,
        "Кажется я потерял контекст :(\nПожалуйста запустите генерацию заново 🔄 или воспользуйтесь меню 📲",
    )


bot.infinity_polling(timeout=60, long_polling_timeout=5)
