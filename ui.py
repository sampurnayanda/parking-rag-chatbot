import streamlit as st

from app.orchestrator import system_graph
from app.chatbot.reservation import get_booked_slots

from app.admin.admin_agent import (
    get_all_reservations,
    get_latest_reservation_status
)


# ── Page Config ───────────────────────────────────────

st.set_page_config(
    page_title="Smart Parking AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ────────────────────────────────────────

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0E1117;
        color: white;
    }

    .block-container {
        padding-top: 80px;
        padding-bottom: 20px;
        padding-left: 50px;
        padding-right: 50px;
    }

    .main-title {
        font-size: 72px;
        font-weight: 800;
        color: #00E5FF;
        text-shadow: 0px 0px 12px rgba(0, 229, 255, 0.6);
        margin-top: 20px;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 22px;
        color: #EEEEEE;
        margin-top: 0px;
    }

    .hero-text {
        font-size: 18px;
        color: #B0B0B0;
        margin-bottom: 20px;
    }

    section[data-testid="stSidebar"] {
        background-color: #1B1F2A;
    }

    .stButton button {
        background-color: #111827;
        color: white;
        border-radius: 14px;
        border: 1px solid #2A2A2A;
        height: 58px;
        font-size: 16px;
        font-weight: 600;
    }

    .stButton button:hover {
        border-color: #00E5FF;
        color: #00E5FF;
        transform: scale(1.02);
        transition: 0.2s;
    }

    .stChatInputContainer {
        border-radius: 16px;
    }

    [data-testid="stChatMessage"] {
        background-color: #111827;
        border-radius: 14px;
        padding: 10px;
        margin-bottom: 10px;
    }

    hr {
        border-color: #2A2A2A;
    }

    .status-card {
        padding: 20px;
        border-radius: 16px;
        background-color: #111827;
        border: 1px solid #2A2A2A;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ── Pricing Config ────────────────────────────────────

VEHICLE_RATES = {
    "🚗 Car":              50,
    "🏍️ Motorcycle":       30,
    "🚙 SUV":              70,
    "⚡ Electric Vehicle":  50,
    "🚚 Truck":            100,
}

VEHICLE_SLOTS = {
    "🚗 Car":              ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2"],
    "🏍️ Motorcycle":       ["M1", "M2", "M3", "M4", "M5"],
    "🚙 SUV":              ["S1", "S2", "S3", "S4"],
    "⚡ Electric Vehicle":  ["EV1", "EV2", "EV3"],
    "🚚 Truck":            ["T1", "T2"],
}


# ── Session State ─────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vehicle_type" not in st.session_state:
    st.session_state.vehicle_type = "🚗 Car"

if "duration" not in st.session_state:
    st.session_state.duration = 1

if "parking_slot" not in st.session_state:
    st.session_state.parking_slot = None

if "pending_input" not in st.session_state:
    st.session_state.pending_input = None


# ── Sidebar ───────────────────────────────────────────

with st.sidebar:

    st.title("🚗 Smart Parking AI")

    st.markdown("---")

    st.markdown("## 🛠️ Booking Preferences")

    vehicle_type = st.selectbox(
        "Vehicle Type",
        options=list(VEHICLE_RATES.keys()),
        index=list(VEHICLE_RATES.keys()).index(
            st.session_state.vehicle_type
        ),
        help="Select your vehicle type — rates and slots vary."
    )
    st.session_state.vehicle_type = vehicle_type

    duration = st.slider(
        "Parking Duration (hours)",
        min_value=1,
        max_value=24,
        value=st.session_state.duration,
        step=1,
        help="How long do you plan to park?"
    )
    st.session_state.duration = duration

    # Filter out already-booked slots
    booked_slots = get_booked_slots()
    all_slots = VEHICLE_SLOTS[vehicle_type]
    available_slots = [
        s for s in all_slots if s not in booked_slots
    ]

    if not available_slots:
        st.warning("⚠️ No available slots for this vehicle type right now.")
        available_slots = all_slots  # fallback to show all

    parking_slot = st.selectbox(
        "Preferred Parking Slot",
        options=available_slots,
        help="Only available slots are shown. Booked slots are hidden."
    )
    st.session_state.parking_slot = parking_slot

    # ── Live cost estimate (single-line HTML — no nesting issues) ──
    rate = VEHICLE_RATES[vehicle_type]
    total_cost = rate * duration
    duration_label = "{}hr{}".format(duration, "s" if duration > 1 else "")
    ev_note = "&nbsp;&nbsp;⚡ EV charging included" if "Electric" in vehicle_type else ""

    st.markdown(
        (
            '<div style="padding:16px 24px;border-radius:14px;'
            'background-color:#0D1F3C;border:1px solid #00E5FF33;'
            'margin-top:12px;margin-bottom:4px;">'
            '<div style="font-size:13px;color:#94A3B8;margin-bottom:4px;">Estimated Cost</div>'
            '<div style="font-size:28px;font-weight:800;color:#00E5FF;">&#8377;{total_cost}</div>'
            '<div style="font-size:12px;color:#64748B;margin-top:4px;">'
            '&#8377;{rate}/hr &times; {duration_label}{ev_note}'
            '</div>'
            '</div>'
        ).format(
            total_cost=total_cost,
            rate=rate,
            duration_label=duration_label,
            ev_note=ev_note,
        ),
        unsafe_allow_html=True
    )

    if st.button("📅 Start Booking Now", use_container_width=True):
        st.session_state["pending_input"] = (
            "book parking | vehicle: {} | slot: {} | duration: {} hours"
        ).format(vehicle_type, parking_slot, duration)
        st.rerun()

    st.markdown("---")

    st.markdown("## ✨ Features")

    st.markdown(
        """
        -  AI Parking Chatbot
        -  RAG Knowledge System
        -  Parking Reservation
        -  Vehicle Type Selection
        -  Slot Selection
        -  Admin Approval
        -  MCP FastAPI Server
        -  LangGraph Workflow
        -  Reservation ID Tracking
        """
    )

    st.markdown("---")

    st.markdown("## ⚡ Example Queries")

    st.markdown(
        """
        - What are parking prices?
        - What are the working hours?
        - Is EV charging available?
        - Which slots are available for SUVs?
        - book parking
        - check reservation RES-8B22207F
        """
    )

    st.markdown("---")

    st.success("🟢 System Online")


# ── Header ────────────────────────────────────────────

st.markdown(
    '<p class="main-title">🚗 Smart Parking AI Platform</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="subtitle">AI-powered parking reservation and management system</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-text"><b>AI Powered Smart Parking Ecosystem</b><br>Secure • Intelligent • Automated • Real-Time</div>',
    unsafe_allow_html=True,
)

st.markdown("---")


# ── Quick Actions ─────────────────────────────────────

QUICK_ACTIONS = [
    (
        "💰 Parking Prices",
        "💰 Parking prices: Car ₹50/hr · Motorcycle ₹30/hr · SUV ₹70/hr · EV ₹50/hr (+ charging) · Truck ₹100/hr"
    ),
    (
        "⚡ EV Charging",
        "⚡ EV charging stations are available at slots EV1, EV2, and EV3 on Level 1."
    ),
    (
        "🕒 Working Hours",
        "🕒 Smart Parking Hub operates 24/7 — open every day, all day."
    ),
    (
        "🅿️ Available Slots",
        "🅿️ Car: A1–C2 · Motorcycle: M1–M5 · SUV: S1–S4 · EV: EV1–EV3 · Truck: T1–T2"
    ),
]

col1, col2, col3, col4 = st.columns(4)

for col, (label, reply) in zip([col1, col2, col3, col4], QUICK_ACTIONS):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
            st.rerun()


# ── Tabs ──────────────────────────────────────────────

tab_chat, tab_status, tab_slots = st.tabs(
    ["💬 Chat", "📋 Reservation Status", "🅿️ Slot Map"]
)


# ── Chat Tab ──────────────────────────────────────────

with tab_chat:

    # ── Render messages first (top) ───────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Chat input (bottom) ───────────────────────────
    user_input = st.chat_input(
        "Ask parking questions or reserve parking..."
    )

    # ── Process pending_input from Start Booking Now button ──
    active_input = user_input
    if not active_input and st.session_state.get("pending_input"):
        active_input = st.session_state.pop("pending_input")
        # Show a user bubble for the button action
        st.session_state.messages.append({
            "role": "user",
            "content": "I want to book parking for my {} at slot {} for {} hour{}.".format(
                st.session_state.vehicle_type,
                st.session_state.parking_slot,
                st.session_state.duration,
                "s" if st.session_state.duration > 1 else "",
            )
        })

    if active_input:

        if active_input == user_input:
            # Normal chat message — add to history
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )

        keywords = ["book", "reserve", "parking slot", "reservation"]
        enriched_input = active_input
        if any(k in active_input.lower() for k in keywords):
            enriched_input = (
                "{} | vehicle: {} | slot: {} | duration: {} hours"
            ).format(
                active_input,
                st.session_state.vehicle_type,
                st.session_state.parking_slot,
                st.session_state.duration,
            )

        state = {
            "user_input": enriched_input,
            "intent": "",
            "response": "",
            "reservation_status": "",
        }

        with st.spinner("AI is processing..."):
            result = system_graph.invoke(state)
            response = result["response"]

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        st.rerun()


# ── Reservation Status Tab ────────────────────────────

with tab_status:

    st.markdown("## 📋 Reservation Status Lookup")

    st.markdown(
        "Search using your unique Reservation ID to view booking details and approval status."
    )

    col_input, col_btn = st.columns([4, 1])

    with col_input:
        reservation_id = st.text_input(
            "Reservation ID",
            placeholder="Enter Reservation ID (e.g. RES-8B22207F)",
            label_visibility="collapsed",
        )

    with col_btn:
        search = st.button("Look up", use_container_width=True)

    if search and reservation_id:
        with st.spinner("Fetching reservation details..."):
            response = get_latest_reservation_status(reservation_id)
        st.code(response)


# ── Slot Map Tab ──────────────────────────────────────

with tab_slots:

    st.markdown("## 🅿️ Parking Slot Map")

    st.markdown(
        "Slots are colour-coded by vehicle type. "
        "Select your vehicle in the sidebar to see which slots apply to you."
    )

    selected = st.session_state.vehicle_type
    booked_slots_map = get_booked_slots()

    slot_config = [
        {
            "label": "🚗 Car Slots",
            "slots": VEHICLE_SLOTS["🚗 Car"],
            "color": "#1E3A5F",
            "border": "#2563EB",
            "highlight": selected == "🚗 Car",
        },
        {
            "label": "🏍️ Motorcycle Slots",
            "slots": VEHICLE_SLOTS["🏍️ Motorcycle"],
            "color": "#1F2D1F",
            "border": "#16A34A",
            "highlight": selected == "🏍️ Motorcycle",
        },
        {
            "label": "🚙 SUV Slots",
            "slots": VEHICLE_SLOTS["🚙 SUV"],
            "color": "#2D1F1F",
            "border": "#DC2626",
            "highlight": selected == "🚙 SUV",
        },
        {
            "label": "⚡ EV Slots (with charging)",
            "slots": VEHICLE_SLOTS["⚡ Electric Vehicle"],
            "color": "#1A2A1A",
            "border": "#00E5FF",
            "highlight": selected == "⚡ Electric Vehicle",
        },
        {
            "label": "🚚 Truck Slots",
            "slots": VEHICLE_SLOTS["🚚 Truck"],
            "color": "#2A2A1A",
            "border": "#D97706",
            "highlight": selected == "🚚 Truck",
        },
    ]

    col_a, col_b = st.columns(2)

    for idx, zone in enumerate(slot_config):

        target_col = col_a if idx % 2 == 0 else col_b

        with target_col:

            border_width = "2px" if zone["highlight"] else "1px"
            glow = "box-shadow: 0 0 12px {}66;".format(zone["border"]) if zone["highlight"] else ""
            your_badge = (
                '&nbsp;<span style="font-size:11px;background:#00E5FF22;'
                'color:#00E5FF;padding:2px 8px;border-radius:10px;">YOUR VEHICLE</span>'
                if zone["highlight"] else ""
            )

            slots_html = "".join(
                (
                    '<span style="display:inline-block;padding:5px 14px;margin:4px;'
                    'border-radius:20px;background:{bg};border:1px solid {bd};'
                    'font-size:13px;font-weight:600;color:{fc};">'
                    '{slot}{tag}</span>'
                ).format(
                    bg="#3B0000" if slot in booked_slots_map else zone["color"],
                    bd="#EF4444" if slot in booked_slots_map else zone["border"],
                    fc="#EF4444" if slot in booked_slots_map else "white",
                    slot=slot,
                    tag=' <span style="font-size:9px;">BOOKED</span>' if slot in booked_slots_map else "",
                )
                for slot in zone["slots"]
            )

            html = (
                '<div style="padding:16px 20px;border-radius:14px;'
                'background-color:{color};border:{bw} solid {border};'
                'margin-bottom:16px;{glow}">'
                '<div style="font-size:15px;font-weight:700;color:white;margin-bottom:10px;">'
                '{label}{badge}'
                '</div>'
                '{slots}'
                '</div>'
            ).format(
                color=zone["color"],
                bw=border_width,
                border=zone["border"],
                glow=glow,
                label=zone["label"],
                badge=your_badge,
                slots=slots_html,
            )

            st.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💰 Rate Summary")

    rate_cols = st.columns(len(VEHICLE_RATES))
    for col, (vtype, vrate) in zip(rate_cols, VEHICLE_RATES.items()):
        with col:
            is_selected = vtype == selected
            border = "#00E5FF" if is_selected else "#2A2A2A"
            bw = "2px" if is_selected else "1px"
            glow = "box-shadow: 0 0 10px #00E5FF44;" if is_selected else ""
            emoji = vtype.split()[0]
            label = " ".join(vtype.split()[1:])
            html = (
                '<div style="text-align:center;padding:14px 8px;border-radius:12px;'
                'background:#111827;border:{bw} solid {border};{glow}">'
                '<div style="font-size:22px;">{emoji}</div>'
                '<div style="font-size:11px;color:#94A3B8;margin-top:4px;">{label}</div>'
                '<div style="font-size:20px;font-weight:800;color:#00E5FF;margin-top:8px;">'
                '&#8377;{rate}<span style="font-size:11px;color:#64748B;">/hr</span>'
                '</div>'
                '</div>'
            ).format(bw=bw, border=border, glow=glow, emoji=emoji, label=label, rate=vrate)
            st.markdown(html, unsafe_allow_html=True)