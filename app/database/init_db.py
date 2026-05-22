import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT,
    surname             TEXT,
    car_number          TEXT,
    reservation_time    TEXT,
    status              TEXT,
    reservation_id      TEXT,
    vehicle_type        TEXT,
    slot                TEXT,
    duration            INTEGER
)
""")

# ── Migration: add new columns if DB already exists ──

existing_columns = [
    row[1]
    for row in cursor.execute("PRAGMA table_info(reservations)")
]

if "reservation_id" not in existing_columns:
    cursor.execute(
        "ALTER TABLE reservations ADD COLUMN reservation_id TEXT"
    )

if "vehicle_type" not in existing_columns:
    cursor.execute(
        "ALTER TABLE reservations ADD COLUMN vehicle_type TEXT"
    )

if "slot" not in existing_columns:
    cursor.execute(
        "ALTER TABLE reservations ADD COLUMN slot TEXT"
    )

if "duration" not in existing_columns:
    cursor.execute(
        "ALTER TABLE reservations ADD COLUMN duration INTEGER"
    )

conn.commit()
conn.close()

print("Database initialized successfully")