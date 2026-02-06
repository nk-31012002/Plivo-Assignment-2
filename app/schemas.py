from pydantic import BaseModel
from typing import Optional, Any

class Message(BaseModel):
    id: str
    payload: Any

class WSRequest(BaseModel):
    type: str  
    topic: Optional[str] = None
    client_id: Optional[str] = None
    message: Optional[Message] = None
    request_id: Optional[str] = None
    last_n: Optional[int] = 0

class TopicCreate(BaseModel):
    name: str