import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz

from app.mcp.mcp_client import send_to_mcp

from app.admin.admin_agent import (
    get_all_reservations,
    update_status,
    cancel_reservation
)

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Smart Parking Admin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- AUTO REFRESH ---------------- #

st_autorefresh(interval=5000, key="admin_refresh")

# ---------------- INDIA TIME ---------------- #

india = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(india)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: white;
}

.block-container {
    padding-top: 50px;
    padding-bottom: 30px;
    padding-left: 50px;
    padding-right: 50px;
}

section[data-testid="stSidebar"] {
    background-color: #1B1F2A;
}

.main-title {
    font-size: 58px;
    font-weight: 800;
    color: #00E5FF;
    text-shadow: 0px 0px 14px rgba(0,229,255,0.6);
    margin-bottom: 10px;
}

.subtitle {
    font-size: 20px;
    color: #CFCFCF;
    margin-bottom: 25px;
}

.stButton button {
    background-color: #111827;
    color: white;
    border-radius: 14px;
    border: 1px solid #2A2A2A;
    height: 52px;
    font-size: 15px;
    font-weight: 600;
}

.stButton button:hover {
    border-color: #00E5FF;
    color: #00E5FF;
    transform: scale(1.02);
    transition: 0.2s;
}

[data-testid="metric-container"] {
    background-color: #111827;
    border: 1px solid #2A2A2A;
    padding: 20px;
    border-radius: 18px;
}

hr {
    border-color: #2A2A2A;
}

.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    background-color: #111827;
    border-radius: 12px;
}

.card-approved { border-left: 5px solid #22C55E; }
.card-rejected { border-left: 5px solid #EF4444; }
.card-pending  { border-left: 5px solid #F59E0B; }

.info-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
    margin-top: 4px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.title("⚙️ Admin Dashboard")
    st.markdown("---")

    st.markdown("## Admin Features")
    st.markdown("""
- Reservation Approval
- Reservation Rejection
- Vehicle Type Visibility
- Slot & Duration Details
- MCP Server Processing
- Reservation Storage
- LangGraph Workflow
- Real-Time Monitoring
""")

    st.markdown("---")
    st.markdown("## Workflow")
    st.markdown("""
1. User selects vehicle type & slot
2. User books parking via chatbot
3. Admin reviews full details
4. Approve or reject
5. MCP server stores reservation
""")

    st.markdown("---")
    st.info(f"🕒 {current_time.strftime('%d %b %Y • %I:%M:%S %p')}")
    st.success("System Online")

# ---------------- HEADER ---------------- #

st.markdown(
    '<p class="main-title">⚙️ Smart Parking Admin Panel</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="subtitle">'
    'Manage parking reservations and approvals in real-time'
    '</p>',
    unsafe_allow_html=True
)
st.markdown("---")

# ---------------- FETCH RESERVATIONS ---------------- #

reservations = get_all_reservations()

reservations = sorted(
    reservations, key=lambda x: x[0], reverse=True
)

# ---------------- COUNTS ---------------- #

pending_count   = sum(1 for r in reservations if r[5] == "PENDING")
approved_count  = sum(1 for r in reservations if r[5] == "APPROVED")
rejected_count  = sum(1 for r in reservations if r[5] == "REJECTED")
cancelled_count = sum(1 for r in reservations if r[5] == "CANCELLED")
total_count     = len(reservations)

# ---------------- METRICS ---------------- #

metric1, metric2, metric3, metric4, metric5 = st.columns(5)

with metric1:
    st.metric("Total", total_count)
with metric2:
    st.metric("Pending", pending_count)
with metric3:
    st.metric("Approved", approved_count)
with metric4:
    st.metric("Rejected", rejected_count)
with metric5:
    st.metric("Cancelled", cancelled_count)

st.markdown("---")

# ---------------- SEARCH ---------------- #

search_query = st.text_input(
    "Search by Reservation ID, Customer Name or Car Number"
)

if search_query:
    reservations = [
        r for r in reservations
        if search_query.lower() in str(r[1]).lower()
        or search_query.lower() in str(r[3]).lower()
        or search_query.lower() in str(r[6]).lower()
    ]

# ---------------- FILTER ---------------- #

filter_option = st.selectbox(
    "Filter Reservations",
    ["ALL", "PENDING", "APPROVED", "REJECTED", "CANCELLED"]
)

if filter_option != "ALL":
    reservations = [
        r for r in reservations if r[5] == filter_option
    ]

st.markdown("---")

# ---------------- EMPTY STATE ---------------- #

if not reservations:
    st.success("✅ No reservations found")

# ---------------- RESERVATION CARDS ---------------- #

for reservation in reservations:

    db_id            = reservation[0]
    name             = reservation[1]
    surname          = reservation[2]
    car_number       = reservation[3]
    reservation_time = reservation[4]
    status           = reservation[5]
    reservation_id   = reservation[6]
    vehicle_type     = reservation[7] or "—"
    slot             = reservation[8] or "—"
    duration         = reservation[9]

    # ---------------- FORMAT DATE ---------------- #

    try:
        formatted_time = datetime.strptime(
            reservation_time, "%Y-%m-%d %H:%M"
        ).strftime("%d %b %Y • %I:%M %p")
    except Exception:
        formatted_time = reservation_time

    # ---------------- COST ESTIMATE ---------------- #

    RATES = {
        "🚗 Car": 50, "🏍️ Motorcycle": 30,
        "🚙 SUV": 70, "⚡ Electric Vehicle": 50,
        "🚚 Truck": 100,
    }
    rate = RATES.get(vehicle_type, 50)
    cost_display = (
        f"₹{rate * duration} "
        f"(₹{rate}/hr × {duration}hr{'s' if duration != 1 else ''})"
        if duration else "—"
    )

    # ---------------- STATUS BADGES ---------------- #

    if status == "APPROVED":
        status_badge = """
        <span style="background-color:#14532D;color:#4ADE80;
        padding:8px 18px;border-radius:20px;font-weight:700;">
        ● APPROVED</span>"""
        card_class = "card-approved"

    elif status == "REJECTED":
        status_badge = """
        <span style="background-color:#7F1D1D;color:#F87171;
        padding:8px 18px;border-radius:20px;font-weight:700;">
        ● REJECTED</span>"""
        card_class = "card-rejected"

    elif status == "CANCELLED":
        status_badge = """
        <span style="background-color:#1E1B4B;color:#A5B4FC;
        padding:8px 18px;border-radius:20px;font-weight:700;">
        ● CANCELLED</span>"""
        card_class = "card-rejected"

    else:
        status_badge = """
        <span style="background-color:#78350F;color:#FBBF24;
        padding:8px 18px;border-radius:20px;font-weight:700;">
        ● PENDING</span>"""
        card_class = "card-pending"

    # ---------------- CARD ---------------- #

    st.markdown(
        f'<div class="{card_class}">',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        info_col, badge_col = st.columns([5, 1])

        with info_col:

            st.markdown(
                f"""
                ### 🚘 Reservation ID: {reservation_id}

                🧑‍💼 **Customer:** {name} {surname}

                🚗 **Car Number:** `{car_number}`

                🗓️ **Reservation Time:** {formatted_time}

                🚘 **Vehicle Type:** {vehicle_type}

                🅿️ **Parking Slot:** {slot}

                ⏱️ **Duration:** {duration} hour{'s' if duration and duration != 1 else ''} &nbsp;|&nbsp; 💰 **Est. Cost:** {cost_display}

                🔹 **Current Status:** {status}
                """,
                unsafe_allow_html=True
            )

        with badge_col:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(status_badge, unsafe_allow_html=True)

        st.markdown("")

        # ---------------- ACTIONS ---------------- #

        if status == "PENDING":

            approve_col, reject_col, cancel_col = st.columns(3)

            with approve_col:
                if st.button(
                    "✅ Approve",
                    use_container_width=True,
                    key=f"approve_{reservation_id}"
                ):
                    with st.spinner("Processing reservation..."):
                        update_status(reservation_id, "APPROVED")
                        send_to_mcp(
                            name,
                            surname,
                            car_number,
                            reservation_time
                        )
                    st.success("Reservation Approved")
                    st.rerun()

            with reject_col:
                if st.button(
                    "❌ Reject",
                    use_container_width=True,
                    key=f"reject_{reservation_id}"
                ):
                    update_status(reservation_id, "REJECTED")
                    st.error("Reservation Rejected")
                    st.rerun()

            with cancel_col:
                if st.button(
                    "🚫 Cancel",
                    use_container_width=True,
                    key=f"cancel_{reservation_id}"
                ):
                    cancel_reservation(reservation_id)
                    st.warning("Reservation Cancelled")
                    st.rerun()

        elif status == "APPROVED":
            if st.button(
                "🚫 Cancel (Admin Override)",
                use_container_width=True,
                key=f"cancel_approved_{reservation_id}"
            ):
                cancel_reservation(reservation_id)
                st.warning("Approved reservation cancelled by admin")
                st.rerun()

        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ---------------- #

st.markdown("---")
st.caption("Smart Parking AI • EPAM Internship Project")