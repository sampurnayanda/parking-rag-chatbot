import sqlite3


# ───────────────────────────────────────────────────────
# GET PENDING RESERVATIONS
# ───────────────────────────────────────────────────────

def get_pending_reservations():

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            surname,
            car_number,
            reservation_time,
            status,
            reservation_id,
            vehicle_type,
            slot,
            duration
        FROM reservations
        WHERE status = 'PENDING'
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


# ───────────────────────────────────────────────────────
# UPDATE STATUS
# ───────────────────────────────────────────────────────

def update_status(reservation_id, status):

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reservations
        SET status = ?
        WHERE reservation_id = ?
    """, (status, reservation_id))

    conn.commit()
    conn.close()


# ───────────────────────────────────────────────────────
# GET LATEST RESERVATION STATUS
# ───────────────────────────────────────────────────────

def get_latest_reservation_status(reservation_id):

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
        ORDER BY id DESC
        LIMIT 1
    """, (reservation_id,))

    row = cursor.fetchone()
    conn.close()

    if row:

        vehicle_line = (
            f"\n🚘 Vehicle Type: {row[6]}" if row[6] else ""
        )
        slot_line = (
            f"\n🅿️ Parking Slot: {row[7]}" if row[7] else ""
        )
        duration_line = (
            f"\n⏱️ Duration: {row[8]} hour"
            f"{'s' if row[8] and row[8] != 1 else ''}"
            if row[8] else ""
        )

        return (
            f"📋 Reservation Details\n\n"
            f"🆔 Reservation ID: {row[0]}\n\n"
            f"👤 Name: {row[1]} {row[2]}\n\n"
            f"🚗 Car Number: {row[3]}\n\n"
            f"📅 Reservation Time: {row[4]}"
            f"{vehicle_line}"
            f"{slot_line}"
            f"{duration_line}\n\n"
            f"📌 Status: {row[5]}"
        )

    return "❌ No reservation found."


# ───────────────────────────────────────────────────────
# CANCEL RESERVATION
# ───────────────────────────────────────────────────────

def cancel_reservation(reservation_id):
    """
    Cancels a reservation by setting its status to CANCELLED.
    Only PENDING reservations can be cancelled by the user.
    Admin can cancel any non-APPROVED reservation.
    Returns a message string.
    """
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status FROM reservations
        WHERE reservation_id = ?
    """, (reservation_id,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return "❌ Reservation not found."

    status = row[0]

    if status == "CANCELLED":
        conn.close()
        return "ℹ️ This reservation is already cancelled."

    cursor.execute("""
        UPDATE reservations
        SET status = 'CANCELLED'
        WHERE reservation_id = ?
    """, (reservation_id,))

    conn.commit()
    conn.close()

    return "✅ Reservation {} has been cancelled successfully.".format(reservation_id)


# ───────────────────────────────────────────────────────
# GET ALL RESERVATIONS
# ───────────────────────────────────────────────────────

def get_all_reservations():

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            surname,
            car_number,
            reservation_time,
            status,
            reservation_id,
            vehicle_type,
            slot,
            duration
        FROM reservations
        ORDER BY id DESC
    """)

    reservations = cursor.fetchall()
    conn.close()

    return reservations