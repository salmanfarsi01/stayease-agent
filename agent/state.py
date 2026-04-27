from typing import TypedDict, Optional, List, Any


class AgentState(TypedDict):
    # The current guest message being processed
    user_message: str

    # Last N messages only — trimmed to keep context window efficient
    messages: List[dict]

    # Unique identifier for this conversation session
    conversation_id: str

    # Classified intent: "search" | "details" | "book" | "escalate"
    intent: Optional[str]

    # Accumulated entities across turns (location, dates, guests, listing_id, etc.)
    extracted_params: Optional[dict]

    # Fields still missing before the tool can be called
    missing_params: Optional[List[str]]

    # Raw result returned by whichever tool was called
    tool_result: Optional[Any]

    # Final response string to send back to the guest
    response: Optional[str]

    # Whether this conversation needs human escalation
    needs_escalation: bool