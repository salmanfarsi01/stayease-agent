import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agent.state import AgentState
from agent.tools import ALL_TOOLS, search_available_properties, get_listing_details, create_booking

_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

CONTEXT_WINDOW = 6  # number of recent messages passed to LLM for context (3-4 turns)

SYSTEM_PROMPT =  """You are StayEase, a friendly accommodation booking assistant for Bangladesh.

You help guests with ONLY these three things:
1. Search available properties (need: location, check_in, check_out, num_guests)
2. Get details about a specific property (need: listing_id)
3. Create a booking (need: listing_id, guest_name, guest_phone, check_in, check_out, num_guests)

Important rules:
- Always respond in English only, never use Bangla.
- If the guest says "hi", "hello", "thanks", "thank you", "ok", "great", or any greeting or closing phrase, respond warmly and politely in English. Do NOT escalate these.
- Only escalate if the request is truly unrelated to property search, details, or booking (e.g. refunds, complaints).
- Prices are always in BDT (Bangladeshi Taka).
- Be conversational and friendly — ask for one or two missing pieces of info at a time.
"""


def _recent_messages(messages: list) -> list:
    """Return the last CONTEXT_WINDOW messages to keep LLM context tight."""
    return messages[-CONTEXT_WINDOW:] if len(messages) > CONTEXT_WINDOW else messages


def _build_lc_history(messages: list) -> list:
    """Convert stored message dicts to LangChain message objects."""
    lc = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in _recent_messages(messages):
        if m["role"] == "user":
            lc.append(HumanMessage(content=m["content"]))
        else:
            lc.append(AIMessage(content=m["content"]))
    return lc


def intent_classifier(state: AgentState) -> AgentState:
    """
    Classify intent and merge any newly extracted params with previously collected ones.
    Uses recent conversation history so the LLM understands multi-turn context.

    Updates: intent, extracted_params
    Next node: check_missing_params (search/details/book) or escalation_handler
    """
    existing_params = state.get("extracted_params") or {}
    history = state.get("messages", [])

    classification_prompt = f"""You are extracting booking intent and parameters from a guest conversation.

Recent conversation:
{json.dumps(_recent_messages(history), ensure_ascii=False)}

Current message: "{state['user_message']}"

Already collected parameters: {json.dumps(existing_params, ensure_ascii=False)}

Instructions:
1. Determine intent: "search", "details", "book", or "escalate"
2. Extract ANY new parameters from the current message
3. Merge with already collected parameters — never drop existing values

Parameter reference:
- search: location, check_in (YYYY-MM-DD), check_out (YYYY-MM-DD), num_guests (int)
- details: listing_id (int)
- book: listing_id (int), guest_name, guest_phone, check_in (YYYY-MM-DD), check_out (YYYY-MM-DD), num_guests (int)

Respond ONLY with valid JSON, no extra text:
{{
  "intent": "search" | "details" | "book" | "escalate",
  "extracted_params": {{}}
}}

Only include fields that have real values. Never include null or empty string values."""

    response = _llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=classification_prompt),
    ])

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw.strip())
        intent = parsed.get("intent", "escalate")
        new_params = parsed.get("extracted_params", {})
        merged = {**existing_params, **{k: v for k, v in new_params.items() if v is not None and v != ""}}
    except (json.JSONDecodeError, IndexError):
        intent = state.get("intent") or "escalate"
        merged = existing_params

    return {**state, "intent": intent, "extracted_params": merged}


def check_missing_params(state: AgentState) -> AgentState:
    """
    Check whether all required params for the current intent are present.
    If anything is missing, ask the guest conversationally for just the missing info.
    Appends the question to messages so history stays accurate.

    Updates: missing_params, response (if asking), messages (if asking)
    Next node: tool_caller (complete) or END (still gathering info)
    """
    intent = state.get("intent")
    params = state.get("extracted_params") or {}
    history = state.get("messages", [])

    required = {
        "search":  ["location", "check_in", "check_out", "num_guests"],
        "details": ["listing_id"],
        "book":    ["listing_id", "guest_name", "guest_phone", "check_in", "check_out", "num_guests"],
    }

    if intent not in required:
        return {**state, "missing_params": []}

    missing = [f for f in required[intent] if not params.get(f)]

    if not missing:
        return {**state, "missing_params": []}

    # Ask for missing info naturally using recent context
    ask_prompt = f"""The guest wants to {intent} a property.

Collected so far: {json.dumps(params, ensure_ascii=False)}
Still missing: {missing}

Write a SHORT, friendly question asking for the missing info.
- Ask for at most 2 things at a time
- Use natural language, not field names (e.g. "check-in date" not "check_in")
- If asking for dates, give a format hint like "e.g. 1 May 2026"
- Match the language the guest is using (Bangla or English)"""

    lc = _build_lc_history(history)
    lc.append(HumanMessage(content=ask_prompt))
    reply = _llm.invoke(lc).content.strip()

    updated_messages = history + [
        {"role": "user",      "content": state["user_message"]},
        {"role": "assistant", "content": reply},
    ]

    return {
        **state,
        "missing_params": missing,
        "response": reply,
        "messages": updated_messages,
    }


def tool_caller(state: AgentState) -> AgentState:
    """
    Invoke the correct tool with fully collected params.
    All params are guaranteed present by check_missing_params.

    Updates: tool_result
    Next node: response_generator
    """
    intent = state["intent"]
    params = state.get("extracted_params") or {}

    try:
        if intent == "search":
            result = search_available_properties.invoke(params)
        elif intent == "details":
            result = get_listing_details.invoke(params)
        elif intent == "book":
            result = create_booking.invoke(params)
        else:
            result = {"error": "No tool for this intent"}
    except Exception as exc:
        result = {"error": str(exc)}

    return {**state, "tool_result": result}


def response_generator(state: AgentState) -> AgentState:
    """
    Generate a natural-language reply from the tool result using recent conversation context.
    After search: lists properties and invites the guest to ask for details or book.
    After booking: confirms with ID and total cost.

    Updates: response, messages
    Next node: END
    """
    tool_result = state.get("tool_result", {})
    history = state.get("messages", [])
    intent = state.get("intent")

    if intent == "search":
        context = f"""Search results: {json.dumps(tool_result, ensure_ascii=False, default=str)}

Present available properties clearly:
- Property name and ID number
- Price per night in BDT
- Max guests and bedrooms
- One short sentence description

Then invite the guest to ask for details on any property or to book one.
If no properties found, apologise and suggest different dates or location."""

    elif intent == "book":
        context = f"""Booking result: {json.dumps(tool_result, ensure_ascii=False, default=str)}

If successful: give a warm confirmation with booking ID, property, dates, and total BDT cost.
If failed: apologise clearly and say what went wrong."""

    else:
        context = f"""Tool result: {json.dumps(tool_result, ensure_ascii=False, default=str)}
Present this clearly and helpfully."""

    lc = _build_lc_history(history)
    lc.append(HumanMessage(content=context))
    reply = _llm.invoke(lc).content.strip()

    updated_messages = history + [
        {"role": "user",      "content": state["user_message"]},
        {"role": "assistant", "content": reply},
    ]

    return {**state, "response": reply, "messages": updated_messages}


def escalation_handler(state: AgentState) -> AgentState:
    """
    Handle out-of-scope requests with a bilingual handoff message.
    Sets needs_escalation=True so the API can alert downstream systems.

    Updates: needs_escalation, response, messages
    Next node: END
    """
    reply = (
        "I'm sorry, I can only help with property search, listing details, and bookings. "
        "Your query is being escalated to a human agent who will assist you shortly."
    )

    updated_messages = (state.get("messages") or []) + [
        {"role": "user",      "content": state["user_message"]},
        {"role": "assistant", "content": reply},
    ]

    return {
        **state,
        "needs_escalation": True,
        "response": reply,
        "messages": updated_messages,
    }


def route_by_intent(state: AgentState) -> str:
    """Route after intent_classifier."""
    if state.get("intent") in ("search", "details", "book"):
        return "check_missing_params"
    return "escalation_handler"


def route_after_param_check(state: AgentState) -> str:
    """Route after check_missing_params — proceed to tool or stop and ask guest."""
    if state.get("missing_params"):
        return "done"
    return "tool_caller"