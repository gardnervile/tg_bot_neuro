from google.cloud import dialogflow_v2 as dialogflow

def detect_intent_text(project_id: str, session_id: str, text: str,
                       language_code: str = "ru", ignore_fallback: bool = False):
    """
    Отправляет текст в Dialogflow и возвращает ответ.
    """
    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session_path, "query_input": query_input}
    )

    if ignore_fallback and response.query_result.intent.is_fallback:
        return None

    return response.query_result.fulfillment_text
