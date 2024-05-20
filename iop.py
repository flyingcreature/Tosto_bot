#Welcome to Input-Output Processer

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
    
    def sing_up(self, id: int):
        ids = [user[1] for user in db.get_all_users_data()]
        if not db.is_user_in_db and MAX_USERS > len(ids):
            db.add_new_user(id)
        else:
            logging.debug("Пользователь уже зарегистрирован")