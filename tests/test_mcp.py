from app.mcp.mcp_client import send_to_mcp


def test_mcp_processing():

    response = send_to_mcp(
        "Test",
        "User",
        "ODTEST123",
        "2026-07-01"
    )

    assert response["status"] == "success"


def test_mcp_response_message():

    response = send_to_mcp(
        "Test",
        "User",
        "ODTEST123",
        "2026-07-01"
    )

    assert "processed" in response["message"].lower()