import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token and MongoDB URL
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is not set")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Initialize MongoDB connection
client = None
db = None
messages_collection = None


async def init_mongo():
    global client, db, messages_collection
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.messages_db
    messages_collection = db.messages


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"Received /start command from user {message.from_user.id}")
    await message.answer(f'''
                          Welcome, {hbold(message.from_user.full_name)}!
                          Use /show_messages to see all messages
                          or simply send a message to create a new one.
                          '''.strip())
    logger.info(f"Sent welcome message to user {message.from_user.id}")


@dp.message(Command("show_messages"))
async def cmd_show_messages(message: types.Message):
    logger.info(f'''
                Received /show_messages command
                from user {message.from_user.id}
                ''')
    try:
        cursor = messages_collection.find().sort("timestamp", -1).limit(20)
        messages = await cursor.to_list(length=20)
        if messages:
            response = "Last 20 messages:\n\n"
            for msg in messages:
                response += f"{hbold(msg.get('username', 'Anonymous'))}: {msg['content']}\n"  # noqa: E501
        else:
            response = "No messages found."
        await message.answer(response)
        logger.info(f"Sent messages list to user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        await message.answer('''An error occurred while fetching messages.
                             Please try again later.
                             ''')


@dp.message()
async def handle_message(message: types.Message):
    logger.info(f'''Received message from user
                {message.from_user.id}: {message.text}
''')
    try:
        new_message = {
            "content": message.text,
            "user_id": str(message.from_user.id),
            "username": message.from_user.username or message.from_user.full_name,  # noqa: E501
            "timestamp": message.date
        }
        await messages_collection.insert_one(new_message)
        await message.answer("Message saved successfully!")
        logger.info(f"Saved message from user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        await message.answer('''An error occurred while saving your message.
                             Please try again later.
                             ''')


async def main():
    logger.info("Starting bot")
    await init_mongo()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
