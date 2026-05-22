from app.orchestrator import system_graph


def test_orchestrator_rag_flow():
    state = {
        "user_input": "What are parking prices?",
        "intent": "",
        "response": "",
        "reservation_status": ""
    }

    result = system_graph.invoke(state)

    assert result["response"] is not None
    assert len(result["response"]) > 0



def test_orchestrator_status_flow():

    state = {
        "user_input": "check status sampurna",
        "intent": "",
        "response": "",
        "reservation_status": ""
    }

    result = system_graph.invoke(state)

    assert "status" in result["response"].lower()