import json
import os
from google.cloud import dialogflow_v2 as dialogflow
from dotenv import load_dotenv

load_dotenv()

project_id = os.environ["PROJECT_ID"]
language_code = "ru"

def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    client = dialogflow.IntentsClient()

    parent = f"projects/{project_id}/agent"

    training_phrases = []
    for phrase in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )

    response = client.create_intent(request={"parent": parent, "intent": intent})
    print(f"✅ Created intent: {display_name} (ID: {response.name})")


def main():
    with open("questions.json", "r", encoding="utf-8") as file:
        questions = json.load(file)

    for intent_name, intent_data in questions.items():
        training_phrases = intent_data["questions"]
        answers = [intent_data["answer"]]

        create_intent(project_id, intent_name, training_phrases, answers)


if __name__ == "__main__":
    main()
