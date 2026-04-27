from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import (
    intent_classifier,
    check_missing_params,
    tool_caller,
    response_generator,
    escalation_handler,
    route_by_intent,
    route_after_param_check,
)


def build_graph() -> StateGraph:
   
    graph = StateGraph(AgentState)

    graph.add_node("intent_classifier",    intent_classifier)
    graph.add_node("check_missing_params", check_missing_params)
    graph.add_node("tool_caller",          tool_caller)
    graph.add_node("response_generator",   response_generator)
    graph.add_node("escalation_handler",   escalation_handler)

    graph.set_entry_point("intent_classifier")

    graph.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "check_missing_params": "check_missing_params",
            "escalation_handler":   "escalation_handler",
        },
    )

    graph.add_conditional_edges(
        "check_missing_params",
        route_after_param_check,
        {
            "tool_caller": "tool_caller",
            "done":        END,
        },
    )

    graph.add_edge("tool_caller",        "response_generator")
    graph.add_edge("response_generator", END)
    graph.add_edge("escalation_handler", END)

    return graph.compile()


agent_graph = build_graph()