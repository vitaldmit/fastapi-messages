from fastapi import APIRouter
from .models import Message
from .database import get_all_messages, create_message

router = APIRouter()


@router.get("/messages/")
async def read_messages():
    messages = await get_all_messages()
    return messages


@router.post("/message/")
async def write_message(message: Message):
    message_id = await create_message(message)
    return {"message": "Message created successfully", "id": message_id}
