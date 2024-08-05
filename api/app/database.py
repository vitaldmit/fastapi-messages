import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId  # noqa: F401


# Load environment variables from .env file
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is not set")

client = AsyncIOMotorClient(MONGO_URL)
db = client.messages_db
messages_collection = db.messages


async def get_all_messages():
    messages = await messages_collection.find().to_list(1000)
    return [
        {**msg, "_id": str(msg["_id"])}
        for msg in messages
    ]


async def create_message(message):
    result = await messages_collection.insert_one(message.dict())
    return str(result.inserted_id)
