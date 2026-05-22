import sqlite3

def init_db():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        available INTEGER
    )
    """)

    # Insert default value if empty
    cursor.execute("SELECT COUNT(*) FROM parking_slots")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO parking_slots (available) VALUES (100)")

    conn.commit()
    conn.close()


def get_availability():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("SELECT available FROM parking_slots LIMIT 1")
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0