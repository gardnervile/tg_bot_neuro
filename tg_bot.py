import logging
import os
import time
from dotenv import load_dotenv

from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dialogflow_client import detect_intent_text
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


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def handle_message(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    response = detect_intent_text(
        project_id=context.bot_data["project_id"],
        session_id=f"tg-{update.effective_chat.id}",
        text=user_text,
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
