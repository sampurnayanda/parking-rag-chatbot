import requests


MCP_URL = (
    "http://127.0.0.1:8000/process_reservation"
)

SECRET_TOKEN = "secure_mcp_token"


def send_to_mcp(
    name,
    surname,
    car_number,
    reservation_time
):

    data = {
        "name": name,
        "surname": surname,
        "car_number": car_number,
        "reservation_time": reservation_time
    }

    response = requests.post(
        MCP_URL,
        params={
            "token": SECRET_TOKEN
        },
        json=data
    )

    return response.json()