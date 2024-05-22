# Welcome to Input-Output Processer
# io.sing_up(message.from_user.id)

# db.add_new_user(DB_TABLE_USERS_NAME, message.chat.id, message.from_user.first_name, 0, None, None, None)
# db.add_new_user(DB_TABLE_USERS_CONGRATULATION, message.chat.id, message.from_user.first_name, None,"МАТЬ", "22.05", "Поздравляю от всей души")


# db.update_row(DB_TABLE_USERS_NAME, message.chat.id, "event", "ДР" )
# db.update_row(DB_TABLE_USERS_CONGRATULATION, message.chat.id, "honored", "Kirill ФФФФ")

# print(db.get_all_users_data(DB_TABLE_USERS_NAME))
# print(db.get_all_users_data(DB_TABLE_USERS_CONGRATULATION))

# print(db.get_user_data(DB_TABLE_USERS_NAME, message.chat.id)["event"])
# print(db.get_user_data(DB_TABLE_USERS_CONGRATULATION, message.chat.id)["honored"])

# print(db.is_user_in_db(DB_TABLE_USERS_NAME, 1645457137))
# print(db.is_user_in_db(DB_TABLE_USERS_CONGRATULATION, 00000000))

# print(db.count_users(DB_TABLE_USERS_NAME, message.chat.id))
# print(db.count_users(DB_TABLE_USERS_CONGRATULATION, message.chat.id))

from config import *
import db, logging
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
        ids = [user[1] for user in db.get_all_users_data()]
        if not db.is_user_in_db and MAX_USERS > len(ids):
            db.add_new_user(DB_TABLE_USERS_NAME, id, first_name, 0, None, None, None)
        else:
            logging.debug("Пользователь уже зарегистрирован")
