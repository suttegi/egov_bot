import logging
import config
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import openai

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!. My Name is Bot. I can have any conversation with you. Please say something!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I can help you with anything!")
    




openai.api_type = "open_ai"
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "Whatever"

messages = [{'role': 'system', 'content': 'You are a helpful assistant. Keep replies within 20 words'}]


async def bot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns the reply to user after getting reply from server."""
    user = update.message.from_user
    
    logger.info("Question from User: %s", update.message.text)
    
    if update.message.text != '':
        user_input = update.message.text
        
        messages.append({'role': 'user', 'content': user_input})
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=messages,
            temperature=0,
            max_tokens=-1
        )
        
        messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        
        llm_reply = response.choices[0].message.content
        
    else:
        return 

    await update.message.reply_text(llm_reply)


def main() -> None:
    application = Application.builder().token(config.TG_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_reply))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()