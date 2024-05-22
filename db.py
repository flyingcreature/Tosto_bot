import logging
import sqlite3

from config import (
    DB_NAME,
    DB_TABLE_USERS_NAME,
    LOGS_PATH,
    DB_TABLE_USERS_CONGRATULATION,
)

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

    except sqlite3.OperationalError as e:
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
            f"long_congratulation TEXT, "
            f"user_birthday TEXT, "
            f"gpt_tokens INTEGER); "
        )
        execute_query(sql_query)
        print("Таблица 1 успешно создана")
        logging.info("Таблица 1 успешно создана")

        sql_query_2 = (
            f"CREATE TABLE {DB_TABLE_USERS_CONGRATULATION} "
            f"(id INTEGER PRIMARY KEY AUTOINCREMENT, "
            f"user_id INTEGER, "
            f"user_name TEXT, "
            f"honored TEXT, "
            f"birthday_honored TEXT, "
            f"text_congratulation TEXT, "
            f"FOREIGN KEY (user_id) REFERENCES {DB_TABLE_USERS_NAME} (user_id)); "
        )
        execute_query(sql_query_2)
        print("Таблица 2 успешно создана")
        logging.info("Таблица 2 успешно создана")

    except Exception as e:
        logging.error(f"Ошибка при создании таблиц: {e}")


def add_new_user(
    table: str,
    user_id: int,
    user_name: str,
    gpt_tokens: int | None,
    honored: str | None,
    birthday_honored: str | None,
    text_congratulation: str | None,
):
    """Функция добавления нового пользователя в базу"""
    if table == DB_TABLE_USERS_NAME:
        if not is_user_in_db(table, user_id):
            sql_query = (
                f"INSERT INTO {DB_TABLE_USERS_NAME} "
                f"(user_id, user_name, gpt_tokens) "
                f"VALUES (?, ?, ?);"
            )
            execute_query(sql_query, (user_id, user_name, gpt_tokens))
            print("Пользователь успешно добавлен в таблицу 1")
            logging.info("Пользователь успешно добавлен в таблицу 1 ")

        else:
            print("Пользователь уже существует!")
            logging.info("Пользователь уже существует!")

    if table == DB_TABLE_USERS_CONGRATULATION:
        sql_query = (
            f"INSERT INTO {DB_TABLE_USERS_CONGRATULATION} "
            f"(user_id, user_name, honored, birthday_honored, text_congratulation) "
            f"VALUES (?, ?, ?, ?, ?);"
        )
        execute_query(
            sql_query,
            (user_id, user_name, honored, birthday_honored, text_congratulation),
        )
        print("Пользователь успешно добавлен в таблицу 2")
        logging.info("Пользователь успешно добавлен в таблицу 2")


def update_row(table: str, user_id: int, column_name: str, new_value: str | int | None):
    """Функция для обновления значения таблицы"""
    if is_user_in_db(table, user_id):
        sql_query = f"UPDATE {table} " f"SET {column_name} = ? " f"WHERE user_id = ?;"

        execute_query(sql_query, (new_value, user_id))

    else:
        print("Пользователь не найден в базе")
        logging.info("Пользователь не найден в базе")


def get_all_users_data(table: str):
    """Функция просмотра таблицы"""
    sql_query = f"SELECT * " f"FROM {table};"

    result = execute_query(sql_query)
    return result


def get_user_data(table: str, user_id: int):
    """Функция для получения конкретной информации от пользователя"""
    if is_user_in_db(table, user_id):
        sql_query = f"SELECT * " f"FROM {table} " f"WHERE user_id = {user_id}"
        row = execute_query(sql_query)[0]
        if table == DB_TABLE_USERS_NAME:
            result = {
                "user_name": row[2],
                "event": row[3],
                "human": row[4],
                "long_tost": row[5],
                "gpt_tokens": row[6],
            }
            return result  # что бы воспользоваться информацией просто пропипши вот так:  gpt_tokens = db.get_user_data(user_id)["gpt_tokens"] и тогда ты получишь токены в переменную gpt_tokens

        if table == DB_TABLE_USERS_CONGRATULATION:
            result = {
                "user_name": row[2],
                "honored": row[3],
                "birthday_honored": row[4],
                "text_congratulation": row[5],
            }
            return result


def is_user_in_db(table: str, user_id: int) -> bool:
    """Функция узнать есть ли пользователь в базе"""
    sql_query = f"SELECT user_id " f"FROM {table} " f"WHERE user_id = ?;"
    return bool(execute_query(sql_query, (user_id,)))


def count_users(table: str, user_id: int):
    """Функция для подсчёта пользователей"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            sql_query = (
                f"SELECT COUNT(DISTINCT user_id) "
                f"FROM {table} "
                f"WHERE user_id <> ?"
            )
            cursor.execute(sql_query, (user_id,))
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        logging.error(f"Ошибка при подсчёте пользователей в бд: {e}")
