from app.chatbot.reservation import (
    ReservationState,
    handle_reservation
)


def test_reservation_start():

    state = ReservationState()

    response = handle_reservation(
        state,
        "book parking"
    )

    assert "name" in response.lower()


def test_reservation_flow():

    state = ReservationState()

    handle_reservation(state, "book parking")

    response1 = handle_reservation(
        state,
        "Sampurna"
    )

    assert "surname" in response1.lower()

    response2 = handle_reservation(
        state,
        "Yanda"
    )

    assert "car number" in response2.lower()


def test_reservation_datetime():

    state = ReservationState()

    handle_reservation(state, "book parking")
    handle_reservation(state, "Sampurna")
    handle_reservation(state, "Yanda")
    handle_reservation(state, "OD02AB1234")

    response = handle_reservation(
        state,
        "2026-05-20 10:00"
    )

    assert "administrator" in response.lower()