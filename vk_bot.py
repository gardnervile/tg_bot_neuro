import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow
import logging

logging.info("✅ Telegram бот запущен")


def detect_intent_text(project_id, session_id, text, language_code="ru"):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    if response.query_result.intent.is_fallback:
        return None
    return response.query_result.fulfillment_text


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
                response_text = detect_intent_text(project_id, str(user_id), user_text, language_code)
            except Exception as e:
                print("Ошибка DialogFlow:", e)
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
