import logging

import requests

from iam_token import get_iam_token

from config import (
    FOLDER_ID,
    GPT_MODEL,
    LOGS_PATH,
    MAX_MODEL_TOKENS,
    URL_GPT,
    URL_TOKENS,
)

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.ERROR,
    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
    filemode="w",
)


def count_tokens_in_dialogue(messages: list) -> int:
    iam_token = get_iam_token()
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json",
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "maxTokens": MAX_MODEL_TOKENS,
        "messages": [],
    }

    for row in messages:
        data["messages"].append({"role": row["role"], "text": row["content"]})
    try:
        result = requests.post(url=URL_TOKENS, json=data, headers=headers)

        return len(result.json()["tokens"])
    except Exception as e:
        print(f"Ошибка при подсчёте токенов{e}")
        logging.error(f"Ошибка при подсчёте токенов{e}")


def get_system_content(event, human, long_tost):
    """Функция, которая собирает строку для system_content"""
    return (
        f"Ты известный ведущий с большим стажем, "
        f"у тебя большой опыт в составлении тостов и поздравлений на различные мероприятия. "
        f"Твоя задача придумать тост на {event}. Поздравлять ты будешь {human}. "
        f"По длине поздравление должно быть {long_tost}. "
        f"Можешь использовать разный фольклор, что бы сделать тост краше."
        f"Не давай никаких инструкций, пользователь знает всё сам."
    )


def ask_gpt_helper(messages) -> str:
    """
    Отправляет запрос к модели GPT с задачей и предыдущим ответом
    для получения ответа или следующего шага
    """
    iam_token = get_iam_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
        "x-folder-id": f"{FOLDER_ID}",
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": MAX_MODEL_TOKENS,
        },
        "messages": [],
    }

    for row in messages:
        data["messages"].append({"role": row["role"], "text": row["content"]})
    try:
        response = requests.post(url=URL_GPT, headers=headers, json=data)
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}.")
        logging.error(f"Произошла непредвиденная ошибка: {e}.")
    else:
        if response.status_code != 200:
            print("Не удалось получить ответ :(")
            logging.error(f"Получена ошибка: {response.json()}")

        else:
            result = response.json()["result"]["alternatives"][0]["message"]["text"]
            messages.append({"role": "assistant", "content": result})
            return result


# Примеры, как работать с gpt. Использовла коенструкции, как нам показывал Миша в боте Генераторе сценариев. Тут механика схожа.
# user_content = "Продолжи историю."  # Формируем user_content
# messages.append({"role": "user", "content": user_content})
# tokens_messages = count_tokens_in_dialogue(messages)
# user_tokens += count_tokens_in_dialogue([{"role": "assistant", "content": answer}])
