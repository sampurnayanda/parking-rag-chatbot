from typing import TypedDict

from app.rag.rag_pipeline import create_rag_pipeline
from app.chatbot.reservation import (
    ReservationState,
    handle_reservation
)
from app.guardrails.filter import guardrail_check

from app.admin.admin_agent import (
    get_latest_reservation_status,
    cancel_reservation
)

from langgraph.graph import StateGraph, END


# ---------------- INIT ---------------- #

qa_chain = create_rag_pipeline()

# Global reservation state
reservation_state = ReservationState()


# ---------------- STATE ---------------- #

class ChatState(TypedDict):
    user_input: str
    intent: str
    response: str


# ---------------- INTENT DETECTION ---------------- #

def detect_intent(user_input: str) -> str:

    text = user_input.lower()

    # Stay in reservation flow
    if reservation_state.step is not None:
        return "reserve"

    # Reservation intent
    if any(k in text for k in [
        "book",
        "reserve",
        "parking slot"
    ]):
        return "reserve"

    # Cancel intent
    if any(k in text for k in ["cancel", "cancellation", "cancel reservation"]):
        return "cancel"

    # Status intent
    if "status" in text:
        return "status"

    return "info"


# ---------------- NODES ---------------- #

def guard_node(state: ChatState) -> ChatState:

    msg = guardrail_check(state["user_input"])

    if msg:
        return {
            **state,
            "intent": "blocked",
            "response": msg
        }

    return state


def intent_classifier_node(
    state: ChatState
) -> ChatState:

    intent = detect_intent(
        state["user_input"]
    )

    return {
        **state,
        "intent": intent
    }


def clean_response(text) -> str:
    """
    Clean Gemma output.
    Gemma always reasons first, then gives the real answer last.
    Strategy: take only the final 1-2 sentences after all the reasoning.
    """
    import re

    # Handle list response
    if isinstance(text, list):
        text = " ".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in text
        )

    text = str(text).strip()

    # Replace literal \n with real newlines
    text = text.replace("\\n", "\n")

    # Split into sentences (rough split on . ! ?)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Filter out reasoning/prompt-echo sentences
    bad_keywords = [
        "role:", "task:", "constraint", "input info:",
        "user question:", "context provided:", "provided text",
        "provided information", "provided parking info",
        "i must state", "since the", "there is no mention",
        "the context", "as a parking assistant",
        "one short sentence", "do not explain",
        "the user asks", "the user is asking",
        "this falls under", "required response",
        "booking process", "no reasoning",
    ]

    clean_sentences = []
    for sent in sentences:
        s = sent.strip()
        if not s:
            continue
        lower = s.lower()
        if any(kw in lower for kw in bad_keywords):
            continue
        # Remove bullet markers
        s = re.sub(r'^[\*\-•]\s+', '', s)
        clean_sentences.append(s)

    if not clean_sentences:
        return "I don't have that information. Please contact smartparking@hub.in"

    # Gemma puts the real answer at the END — take last 2 sentences max
    result = " ".join(clean_sentences[-2:]).strip()
    return result


def rag_node(state: ChatState) -> ChatState:

    # qa_chain is now a plain callable, not a LangChain chain
    result = qa_chain({"query": state["user_input"]})

    return {
        **state,
        "response": clean_response(result["result"])
    }


def reservation_node(
    state: ChatState
) -> ChatState:

    reply = handle_reservation(
        reservation_state,
        state["user_input"]
    )

    return {
        **state,
        "response": reply
    }


def cancel_node(state: ChatState) -> ChatState:

    user_input = state["user_input"]

    # Extract reservation ID — look for RES- pattern
    import re
    match = re.search(r"RES-[A-Z0-9]+", user_input.upper())

    if not match:
        return {
            **state,
            "response": (
                "Please provide your Reservation ID to cancel. "
                "Example: cancel reservation RES-8B22207F"
            )
        }

    reservation_id = match.group()
    result = cancel_reservation(reservation_id)

    return {
        **state,
        "response": result
    }


def status_node(state: ChatState) -> ChatState:

    words = state["user_input"].split()

    if len(words) < 2:
        return {
            **state,
            "response": "Please provide your name."
        }

    name = words[-1]

    status = get_latest_reservation_status(name)

    return {
        **state,
        "response": f"Your reservation status is: {status}"
    }


# ---------------- ROUTER ---------------- #

def router(state: ChatState):

    if state["intent"] == "blocked":
        return "end"

    if state["intent"] == "reserve":
        return "reserve"

    if state["intent"] == "cancel":
        return "cancel"

    if state["intent"] == "status":
        return "status"

    return "rag"


# ---------------- GRAPH ---------------- #

graph = StateGraph(ChatState)

graph.add_node("guard", guard_node)

graph.add_node(
    "intent_classifier",
    intent_classifier_node
)

graph.add_node("rag", rag_node)

graph.add_node("reserve", reservation_node)

graph.add_node("cancel", cancel_node)

graph.add_node("status", status_node)

# Entry
graph.set_entry_point("guard")

# Guard → intent classifier (always)
graph.add_edge("guard", "intent_classifier")

# Intent classifier → route
graph.add_conditional_edges(
    "intent_classifier",
    router,
    {
        "reserve": "reserve",
        "cancel": "cancel",
        "status": "status",
        "rag": "rag",
        "end": END,
    }
)

# End points
graph.add_edge("rag", END)
graph.add_edge("reserve", END)
graph.add_edge("cancel", END)
graph.add_edge("status", END)

# Compile
chatbot_app = graph.compile()


# ---------------- CHAT FUNCTION ---------------- #

def chat(user_input: str):

    state = {
        "user_input": user_input,
        "intent": "",
        "response": ""
    }

    result = chatbot_app.invoke(state)

    return result["response"]