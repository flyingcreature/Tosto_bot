from os import getenv

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("token")  # Токен бота

FOLDER_ID = getenv("folder_id")  # Folder_id для gpt

IAM_TOKEN = getenv("iam_token")  # Iam токен для gpt

LOGS_PATH = f"log_file.txt"  # Путь к файлу логов

ADMINS = [1645457137, 786540182, 6303315695]  # Список user_id админов

MAX_USER_GPT_TOKENS = 5000  # 5 000 токенов для генерации текста

DB_NAME = f"db.sqlite"  # файл для базы данных

DB_TABLE_USERS_NAME = (
    "users"  # Название таблицы, где хранятся данные для создания поздравления
)

DB_TABLE_USERS_CONGRATULATION = (
    "congratulation"  # Название таблицы, где хранятся поздравления пользователя
)

GPT_MODEL = "yandexgpt"  # Модель gpt

IAM_TOKEN_ENDPOINT = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"  # Адресс токена

IAM_TOKEN_PATH = f"token_data.json"  # Путь к json файлу с ключом

URL_TOKENS = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"  # Ссылка на токены gpt

URL_GPT = (
    "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"  # Ссылка на gpt
)
