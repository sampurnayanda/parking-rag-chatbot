from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

APPROVED_FILE = "approved_reservations.txt"

SECRET_TOKEN = "secure_mcp_token"


# ---------------- REQUEST MODEL ---------------- #

class ReservationRequest(BaseModel):

    name: str
    surname: str
    car_number: str
    reservation_time: str


# ---------------- MCP ENDPOINT ---------------- #

@app.post("/process_reservation")

def process_reservation(
    reservation: ReservationRequest,
    token: str
):

    # Security check
    if token != SECRET_TOKEN:

        return {
            "status": "error",
            "message": "Unauthorized access"
        }

    approval_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    entry = (
        f"{reservation.name} "
        f"{reservation.surname} | "
        f"{reservation.car_number} | "
        f"{reservation.reservation_time} | "
        f"{approval_time}\n"
    )

    with open(
        APPROVED_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(entry)

    return {
        "status": "success",
        "message": "Reservation processed"
    }