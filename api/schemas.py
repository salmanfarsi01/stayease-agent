from typing import List, Optional, Any
from pydantic import BaseModel, Field



class MessageItem(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The guest's message text")


class SendMessageResponse(BaseModel):
    conversation_id: str
    reply: str = Field(..., description="Agent's response to the guest")
    intent: Optional[str] = Field(None, description="Classified intent of the message")
    tool_result: Optional[Any] = Field(None, description="Raw data returned by the tool")
    needs_escalation: bool = Field(False, description="True if routed to a human agent")



class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[MessageItem]
    needs_escalation: bool



class ErrorResponse(BaseModel):
    detail: str
