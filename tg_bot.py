import logging
import os
import time
from dotenv import load_dotenv

from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from google.cloud import dialogflow_v2 as dialogflow

logger = logging.getLogger(__name__)

class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.bot.send_message(chat_id=self.chat_id, text=f"⚠️ {log_entry}", timeout=3)
        except Exception:
            pass


def detect_intent_text(project_id: str, session_id: str, text: str, language_code: str = "ru") -> str:
    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    request = {
        "session": session_path,
        "query_input": query_input
    }

    response = session_client.detect_intent(request=request)
    return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def handle_message(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    response = detect_intent_text(
        text=user_text,
        project_id=context.bot_data["project_id"],
        session_id=str(update.effective_chat.id),
        language_code="ru"
    )
    update.message.reply_text(response)


def main() -> None:
    load_dotenv()
    telegram_token = os.environ['TG_TOKEN']
    chat_id = int(os.environ['CHAT_ID'])
    project_id = os.environ["PROJECT_ID"]

    bot = Bot(token=telegram_token)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    telegram_handler = TelegramLogsHandler(bot, chat_id)
    telegram_handler.setFormatter(formatter)
    logger.addHandler(telegram_handler)

    logger.info("✅ Telegram бот запускается...")

    while True:
        try:
            updater = Updater(token=telegram_token)
            dispatcher = updater.dispatcher

            dispatcher.bot_data["project_id"] = project_id
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

            logger.info("✅ Telegram бот запущен")
            updater.start_polling()
            updater.idle()

        except Exception:
            logger.exception("❌ Бот упал с ошибкой:")
            time.sleep(5)


if __name__ == '__main__':
    main()
