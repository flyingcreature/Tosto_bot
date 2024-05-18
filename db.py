import logging
import sqlite3

from config import DB_NAME, DB_TABLE_USERS_NAME, LOGS_PATH

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.ERROR,
    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
    filemode="w",
)


def create_db():
    connection = sqlite3.connect(DB_NAME)
    connection.close()


def execute_query(query: str, data: tuple | None = None, db_name: str = DB_NAME):
    """
    Функция для выполнения запроса к базе данных.
    Принимает имя файла базы данных, SQL-запрос и опциональные данные для вставки.
    """
    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
            connection.commit()

        else:
            cursor.execute(query)

    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса: ", e)
        logging.error("Ошибка при выполнении запроса: ", e)

    else:
        result = cursor.fetchall()
        connection.close()
        return result


def create_table():
    """
    Функция для создания таблицы.
    """
    try:
        sql_query = (
            f"CREATE TABLE IF NOT EXISTS {DB_TABLE_USERS_NAME} "
            f"(id INTEGER PRIMARY KEY, "
            f"user_id INTEGER, "
            f"user_name TEXT, "
            f"event TEXT, "
            f"human TEXT, "
            f"long_tost TEXT, "
            f"gpt_tokens INTEGER); "
        )
        execute_query(sql_query)
        print("Таблица успешно создана")
        logging.info("Таблица успешно создана")

    except Exception as e:
        logging.error(
            f"Ошибка при создании таблицы: {e}"
        )


def add_new_user(user_id: int):
    """Функция добавления нового пользователя в базу"""
    if not is_user_in_db(user_id):
        sql_query = (
            f"INSERT INTO {DB_TABLE_USERS_NAME} " 
            f"(user_id, user_name, gpt_tokens) "
            f"VALUES (?, ?, {0});"
        )
        execute_query(sql_query, (user_id,))
        print("Пользователь успешно добавлен")
        logging.info("Пользователь успешно добавлен")
    else:
        print("Пользователь уже существует!")
        logging.info("Пользователь уже существует!")


def update_row(user_id: int, column_name: str, new_value: str | int | None):
    """Функция для обновления значения таблицы"""
    if is_user_in_db(user_id):
        sql_query = (
            f"UPDATE {DB_TABLE_USERS_NAME} "
            f"SET {column_name} = ? "
            f"WHERE user_id = ?;"
        )

        execute_query(sql_query, (new_value, user_id))

    else:
        print("Пользователь не найден в базе")
        logging.info("Пользователь не найден в базе")


def get_all_users_data():
    """Функция для предоставления информации о пользователе"""
    sql_query = f"SELECT * " f"FROM {DB_TABLE_USERS_NAME};"

    result = execute_query(sql_query)
    return result


def is_user_in_db(user_id: int) -> bool:
    """Функция узнать есть ли пользователь в базе"""
    sql_query = f"SELECT user_id " f"FROM {DB_TABLE_USERS_NAME} " f"WHERE user_id = ?;"
    return bool(execute_query(sql_query, (user_id,)))


def count_users(user_id):
    """Функция для подсчёта пользователей"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            sql_query = (
                f"SELECT COUNT(DISTINCT user_id) "
                f"FROM {DB_TABLE_USERS_NAME} "
                f"WHERE user_id <> ?"
            )
            cursor.execute(sql_query, (user_id,))
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        logging.error(
            f"Ошибка при подсчёте пользователей в бд: {e}"
        )
