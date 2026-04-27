import traceback
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Conversation
from api.schemas import (
    SendMessageRequest,
    SendMessageResponse,
    ConversationHistoryResponse,
    MessageItem,
)
from agent.graph import agent_graph
from agent.state import AgentState

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post(
    "/{conversation_id}/message",
    response_model=SendMessageResponse,
    status_code=status.HTTP_200_OK,
)
async def send_message(
    conversation_id: str,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
) -> SendMessageResponse:
    try:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            conversation = Conversation(
                id=conversation_id,
                messages=[],
                needs_escalation=0,
                intent=None,
                extracted_params={},
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        initial_state: AgentState = {
            "user_message": body.message,
            "messages": conversation.messages or [],
            "conversation_id": conversation_id,
            "intent": conversation.intent,
            "extracted_params": conversation.extracted_params or {},
            "missing_params": None,
            "tool_result": None,
            "response": None,
            "needs_escalation": bool(conversation.needs_escalation),
        }

        final_state: AgentState = agent_graph.invoke(initial_state)
        logger.info(f"Agent done. intent={final_state.get('intent')}")

        conversation.messages = final_state["messages"]
        conversation.needs_escalation = 1 if final_state["needs_escalation"] else 0
        conversation.intent = final_state.get("intent")
        conversation.extracted_params = final_state.get("extracted_params") or {}
        db.commit()

        return SendMessageResponse(
            conversation_id=conversation_id,
            reply=final_state["response"] or "",
            intent=final_state.get("intent"),
            tool_result=final_state.get("tool_result"),
            needs_escalation=final_state["needs_escalation"],
        )

    except Exception as exc:
        traceback.print_exc()
        logger.error(f"send_message error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/{conversation_id}/history",
    response_model=ConversationHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_history(
    conversation_id: str,
    db: Session = Depends(get_db),
) -> ConversationHistoryResponse:
    try:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found.",
            )

        messages = [
            MessageItem(role=m["role"], content=m["content"])
            for m in (conversation.messages or [])
        ]

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            needs_escalation=bool(conversation.needs_escalation),
        )

    except HTTPException:
        raise
    except Exception as exc:
        traceback.print_exc()
        logger.error(f"get_history error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )