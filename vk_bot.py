import vk_api
import os
import logging
import traceback

from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow
from dialogflow_client import detect_intent_text


logging.info("✅ Telegram бот запущен")


def main():
    load_dotenv()

    vk_token = os.environ["VK_TOKEN"]
    project_id = os.environ["PROJECT_ID"]
    language_code = "ru"
    credentials_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            user_text = event.text

            try:
                response_text = detect_intent_text(
                    project_id,
                    f"vk-{user_id}",
                    user_text,
                    language_code,
                    ignore_fallback=True
                )

            except Exception as e:
                traceback.print_exc()
                continue

            if not response_text:
                continue

            vk.messages.send(
                user_id=user_id,
                message=response_text,
                random_id=vk_api.utils.get_random_id()
            )


if __name__ == "__main__":
    main()
