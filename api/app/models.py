from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Message(BaseModel):
    content: str
    user_id: str
    username: Optional[str]
    timestamp: datetime = datetime.utcnow()
