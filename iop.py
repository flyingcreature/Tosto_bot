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
        db.add_new_user(DB_TABLE_USERS_NAME, id, first_name, 0, 3)
        db.add_new_user(DB_TABLE_USERS_CONGRATULATION, id, first_name)


    def updd_pgen(self, id: int, event: str, name: str, date: float):
        db.update_row(DB_TABLE_USERS_NAME, id, "event", event)
        db.update_row(DB_TABLE_USERS_NAME, id, "human", name)
        db.update_row(DB_TABLE_USERS_CONGRATULATION, id, "birthday_honored", date)
        db.update_row(DB_TABLE_USERS_CONGRATULATION, id, "honored", name)

    def generate(self, user_id: int):
        event = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["event"]
        human = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["human"]
        long = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["long_congratulation"]
        tokens = db.get_user_data(DB_TABLE_USERS_NAME, user_id)["gpt_tokens"]

        prompt = [
            {"role": "system", "content": gpt.get_system_content(event, human, long)}
        ]
        prompt.append({"role": "user", "content": "Составь тост."})
        answer = gpt.ask_gpt_helper(prompt)
        if answer == "cd_error":
            return answer
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
    
class Monetize(IOP):
    def gpt_rate(self, tokens: int) -> float:
        return tokens * (0.20 / 1000)

    def speechkit_recog_rate(self, blocks: int) -> float:
        return blocks * 0.16

    def speechkit_synt_rate(self, symbols: int) -> float:
        return float(symbols * (1320 / 1000000))

    def cost_calculation(self, idp: int, typed: str) -> float:
        user = db.get_user_data(DB_TABLE_USERS_NAME, idp)
        gpt_limit = int(user.get("gpt_tokens"))
        if typed == "gpt":
            return self.gpt_rate(gpt_limit)
        else:
            Exception("Неверный тип технологии для вычисления стоймости")

                