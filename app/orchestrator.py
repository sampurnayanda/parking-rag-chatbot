from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    END
)

from app.chatbot.chatbot import (
    chat,
    detect_intent
)

from app.admin.admin_agent import (
    get_latest_reservation_status
)


# ---------------- STATE ---------------- #

class SystemState(TypedDict):

    user_input: str

    intent: str

    response: str

    reservation_status: str


# ---------------- NODES ---------------- #

def intent_node(
    state: SystemState
):

    intent = detect_intent(
        state["user_input"]
    )

    return {
        **state,
        "intent": intent
    }


def chatbot_node(
    state: SystemState
):

    response = chat(
        state["user_input"]
    )

    return {
        **state,
        "response": response
    }


def admin_node(
    state: SystemState
):

    words = state["user_input"].split()

    name = words[-1]

    status = (
        get_latest_reservation_status(name)
    )

    return {
        **state,
        "reservation_status": status,
        "response":
            f"Your reservation status is: {status}"
    }




# ---------------- ROUTER ---------------- #

def router(state: SystemState):

    if state["intent"] == "status":
        return "admin"

    if state["intent"] == "reserve":
        return "chatbot"

    return "chatbot"


# ---------------- GRAPH ---------------- #

graph = StateGraph(SystemState)

graph.add_node(
    "intent_classifier",
    intent_node
)

graph.add_node(
    "chatbot",
    chatbot_node
)

graph.add_node(
    "admin",
    admin_node
)



graph.set_entry_point("intent_classifier")

graph.add_conditional_edges(
    "intent_classifier",
    router,
    {
        "chatbot": "chatbot",
        "admin": "admin"
    }
)

graph.add_edge("chatbot", END)

graph.add_edge("admin", END)


system_graph = graph.compile()