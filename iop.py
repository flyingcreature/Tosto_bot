from config import *
import db, logging, telebot
import yandex_gpt as gpt

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)


class IOP:
    def __init__(self) -> None:
        db.create_table()

    def sing_up(self, id: int, first_name: str):
        ids = [user[1] for user in db.get_all_users_data(DB_TABLE_USERS_NAME)]
        if not db.is_user_in_db and MAX_USERS > len(ids):
            db.add_new_user(DB_TABLE_USERS_NAME, id, first_name, 0)
            db.add_new_user(DB_TABLE_USERS_CONGRATULATION, id, first_name)
        else:
            logging.debug("Пользователь уже зарегистрирован")

    def updd_pgen(self, id: int, event: str, name: str, date: float):
        db.update_row(DB_TABLE_USERS_NAME, id, "event", event)
        db.update_row(DB_TABLE_USERS_NAME, id, "human", name)
        db.update_row(DB_TABLE_USERS_CONGRATULATION, id, "birthday_honored", date)
        db.update_row(DB_TABLE_USERS_CONGRATULATION, id, "honored", name)

    def generate(self, user_id: int):
        event = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["event"]
        human = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["human"]
        long = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["long_tost"]
        tokens = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["gpt_tokens"]

        prompt = [
            {"role": "system", "content": gpt.get_system_content(event, human, long)}
        ]
        prompt.append({"role": "user", "content": "Составь тост."})
        answer = gpt.ask_gpt_helper(prompt)
        prompt.append({"role": "assistant", "content": answer})
        current_tokens_used = gpt.count_tokens_in_dialogue(prompt)
        db.update_row(
            DB_TABLE_USERS_NAME, user_id, "gpt_tokens", tokens + current_tokens_used
        )
        db.update_row(
            DB_TABLE_USERS_CONGRATULATION, user_id, "text_congratulation", answer
        )
        return answer

    def last_gen(self, user_id: int):
        return db.get_user_data(DB_TABLE_USERS_CONGRATULATION, user_id)["text_congratulation"], db.get_user_data(DB_TABLE_USERS_CONGRATULATION, user_id)["birthday_honored"]
    
    def get_inline_keyboard(
        self, values: tuple[tuple[str, str],...]
    ) -> telebot.types.InlineKeyboardMarkup:
        """
        Creates an inline keyboard markup.

        Args:
            values (tuple[tuple[str, str]]): The values for the inline keyboard buttons.

        Returns:
            telebot.types.InlineKeyboardMarkup: The created inline keyboard markup.
        """
        markup = telebot.types.InlineKeyboardMarkup()
        for value in values:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    text=value[0], callback_data=value[1]
                )
            )
        return markup

                