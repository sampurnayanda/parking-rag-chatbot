import sqlite3
import uuid
from datetime import datetime


class ReservationState:

    def __init__(self):
        self.reset()

    def reset(self):
        self.step          = None
        self.name          = ""
        self.surname       = ""
        self.car_number    = ""
        self.datetime      = ""
        self.vehicle_type  = ""
        self.slot          = ""
        self.duration      = 0


# ───────────────────────────────────────────────────────
# PARSE CONTEXT FROM ENRICHED MESSAGE
# e.g. "book parking | vehicle: Car | slot: A1 | duration: 2 hours"
# ───────────────────────────────────────────────────────

def parse_booking_context(user_input):
    context = {
        "vehicle_type": "",
        "slot":         "",
        "duration":     0,
    }

    if "|" not in user_input:
        return context

    parts = user_input.split("|")

    for part in parts:
        part = part.strip()
        if part.lower().startswith("vehicle:"):
            context["vehicle_type"] = part.split(":", 1)[1].strip()
        elif part.lower().startswith("slot:"):
            context["slot"] = part.split(":", 1)[1].strip()
        elif part.lower().startswith("duration:"):
            raw = part.split(":", 1)[1].strip()
            try:
                context["duration"] = int(raw.split()[0])
            except (ValueError, IndexError):
                context["duration"] = 0

    return context


# ───────────────────────────────────────────────────────
# SLOT AVAILABILITY CHECK
# ───────────────────────────────────────────────────────

def is_slot_available(slot, reservation_time):
    """
    Returns True if the slot has no PENDING or APPROVED
    reservation at the given date (YYYY-MM-DD).
    Checks date only — same slot on a different day is fine.
    """
    if not slot:
        return True

    date_only = reservation_time.split(" ")[0]

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM reservations
        WHERE slot = ?
          AND reservation_time LIKE ?
          AND status IN ('PENDING', 'APPROVED')
    """, (slot, date_only + "%"))

    count = cursor.fetchone()[0]
    conn.close()

    return count == 0


# ───────────────────────────────────────────────────────
# GET BOOKED SLOTS (for ui.py dropdown filtering)
# ───────────────────────────────────────────────────────

def get_booked_slots():
    """
    Returns a set of slot names that currently have
    a PENDING or APPROVED reservation.
    """
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT slot FROM reservations
        WHERE status IN ('PENDING', 'APPROVED')
          AND slot IS NOT NULL
          AND slot != ''
          AND status != 'CANCELLED'
    """)

    rows = cursor.fetchall()
    conn.close()

    return {row[0] for row in rows}


# ───────────────────────────────────────────────────────
# BOOK RESERVATION
# ───────────────────────────────────────────────────────

def handle_reservation(state, user_input):

    # ── Start Booking ─────────────────────────────────

    if state.step is None:

        context = parse_booking_context(user_input)
        state.vehicle_type = context["vehicle_type"]
        state.slot         = context["slot"]
        state.duration     = context["duration"]

        state.step = "name"
        return "Enter your name:"

    # ── Name ──────────────────────────────────────────

    elif state.step == "name":
        state.name = user_input
        state.step = "surname"
        return "Enter your surname:"

    # ── Surname ───────────────────────────────────────

    elif state.step == "surname":
        state.surname = user_input
        state.step = "car_number"
        return "Enter your car number:"

    # ── Car Number ────────────────────────────────────

    elif state.step == "car_number":
        state.car_number = user_input
        state.step = "datetime"
        return (
            "Enter reservation date & time "
            "(YYYY-MM-DD HH:MM):"
        )

    # ── Date & Time ───────────────────────────────────

    elif state.step == "datetime":

        try:
            reservation_time = datetime.strptime(
                user_input, "%Y-%m-%d %H:%M"
            )
            current_time = datetime.now()

            if reservation_time <= current_time:
                return (
                    "❌ Reservation date & time "
                    "must be in the future."
                )

        except ValueError:
            return (
                "❌ Invalid format.\n"
                "Use YYYY-MM-DD HH:MM"
            )

        state.datetime = user_input

        # ── Slot availability check ──────────────────

        if state.slot and not is_slot_available(state.slot, state.datetime):
            taken_slot = state.slot
            state.reset()
            return (
                "❌ Sorry, slot **{}** is already booked for that date.\n\n"
                "Please go back to the sidebar, choose a different slot, "
                "and try booking again."
            ).format(taken_slot)

        # ── Generate Reservation ID ──────────────────

        reservation_id = (
            "RES-" + str(uuid.uuid4())[:8].upper()
        )

        # ── Pricing ──────────────────────────────────

        RATES = {
            "Car":              50,
            "Motorcycle":       30,
            "SUV":              70,
            "Electric Vehicle":  50,
            "Truck":            100,
        }

        # Strip emoji from vehicle_type for rate lookup
        vtype_clean = state.vehicle_type
        for key in RATES:
            if key in vtype_clean:
                rate = RATES[key]
                break
        else:
            rate = 50

        estimated_cost = rate * state.duration if state.duration else None

        # ── Save to Database ─────────────────────────

        conn = sqlite3.connect("parking.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO reservations
            (
                reservation_id,
                name,
                surname,
                car_number,
                reservation_time,
                status,
                vehicle_type,
                slot,
                duration
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reservation_id,
            state.name,
            state.surname,
            state.car_number,
            state.datetime,
            "PENDING",
            state.vehicle_type,
            state.slot,
            state.duration,
        ))

        conn.commit()
        conn.close()

        # ── Success Response ─────────────────────────

        vehicle_line = (
            "\n🚘 Vehicle Type: {}".format(state.vehicle_type)
            if state.vehicle_type else ""
        )
        slot_line = (
            "\n🅿️ Parking Slot: {}".format(state.slot)
            if state.slot else ""
        )
        duration_line = (
            "\n⏱️ Duration: {} hour{}".format(
                state.duration, "s" if state.duration != 1 else ""
            )
            if state.duration else ""
        )
        cost_line = (
            "\n💰 Estimated Cost: ₹{}".format(estimated_cost)
            if estimated_cost else ""
        )

        response = (
            "✅ Reservation request sent for administrator approval.\n\n"
            "🆔 Your Reservation ID: **{}**"
            "{}{}{}{}\n\n"
            "📌 Please save this ID for future tracking."
        ).format(
            reservation_id,
            vehicle_line,
            slot_line,
            duration_line,
            cost_line,
        )

        state.reset()
        return response


# ───────────────────────────────────────────────────────
# CHECK RESERVATION STATUS
# ───────────────────────────────────────────────────────

def check_reservation_status(reservation_id):

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            reservation_id,
            name,
            surname,
            car_number,
            reservation_time,
            status,
            vehicle_type,
            slot,
            duration
        FROM reservations
        WHERE reservation_id = ?
    """, (reservation_id,))

    row = cursor.fetchone()
    conn.close()

    if row:

        vehicle_line = (
            "\n🚘 Vehicle Type: {}".format(row[6]) if row[6] else ""
        )
        slot_line = (
            "\n🅿️ Parking Slot: {}".format(row[7]) if row[7] else ""
        )
        duration_line = (
            "\n⏱️ Duration: {} hour{}".format(
                row[8], "s" if row[8] and row[8] != 1 else ""
            )
            if row[8] else ""
        )

        return (
            "📋 Reservation Details\n\n"
            "🆔 Reservation ID: {}\n\n"
            "👤 Name: {} {}\n\n"
            "🚗 Car Number: {}\n\n"
            "📅 Reservation Time: {}"
            "{}{}{}\n\n"
            "📌 Status: {}"
        ).format(
            row[0], row[1], row[2], row[3], row[4],
            vehicle_line, slot_line, duration_line, row[5]
        )

    return "❌ Reservation not found."