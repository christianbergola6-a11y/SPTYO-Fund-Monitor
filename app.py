import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# ==========================================
# 🎨 SPTYO COLORS
# ==========================================
PRIMARY_COLOR = "#1A1A1A"
GOLD_COLOR    = "#D4AF37"
CREAM_COLOR   = "#F8F4E9"
GREEN_ACCENT  = "#34A853"
RED_ACCENT    = "#EA4335"
YELLOW_ACCENT = "#FBBC05"
BLUE_ACCENT   = "#4285F4"
TEXT_COLOR    = "#2C2C2C"

# ==========================================
# 🔑 YOUR SUPABASE KEYS
# ==========================================
SUPABASE_URL = "https://rfyonjupxgficvqjolph.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJmeW9uanVweGdmaWN2cWpvbHBoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY1MDEzODgsImV4cCI6MjEwMjA3NzM4OH0.XTrHlteEeHoBaZ_HAvExDdGqwDHRjY0ubMmswz4MqQ8"

# ==========================================
# 🔐 LOGIN
# ==========================================
ALLOWED_USERS = {
    "President": "SPTYOpresident",
    "Vice President": "SPTYOvicepresident"
}

# ==========================================
# 🚀 CONNECT TO DATABASE
# ==========================================
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except:
        url = SUPABASE_URL
        key = SUPABASE_KEY
    return create_client(url, key)

supabase = init_db()

# ==========================================
# 🎨 PAGE STYLE
# ==========================================
st.set_page_config(page_title="SPTYO Fund Monitor", page_icon="💰", layout="wide")
st.markdown(f"""
    <style>
    .stApp {{background-color: {CREAM_COLOR}; color: {TEXT_COLOR};}}
    h1, h2, h3 {{color: {PRIMARY_COLOR}; font-weight: 700;}}
    .stButton>button {{
        background: linear-gradient(90deg, {GOLD_COLOR}, {YELLOW_ACCENT});
        color: {PRIMARY_COLOR}; border-radius: 12px; border: 2px solid {PRIMARY_COLOR};
        font-weight: bold; padding: 0.4rem 1rem;
    }}
    .stButton>button[kind="secondary"] {{
        background: linear-gradient(90deg, {RED_ACCENT}, #ff6b6b);
        color: white; border: none;
    }}
    .metric-card {{
        background: linear-gradient(135deg, #FFFFFF, {CREAM_COLOR});
        border: 3px solid {GOLD_COLOR}; border-radius: 16px;
        padding: 2rem; box-shadow: 4px 6px 0px {PRIMARY_COLOR}25; text-align: center;
    }}
    .balance-text {{font-size: 2.5rem; font-weight: 900; color: {PRIMARY_COLOR};}}
    .rainbow-line {{
        height: 6px; border-radius: 3px;
        background: linear-gradient(90deg, {RED_ACCENT}, {YELLOW_ACCENT}, {GREEN_ACCENT}, {BLUE_ACCENT});
    }}
    hr {{border: none; height: 3px; background: linear-gradient(90deg, {GOLD_COLOR}, {PRIMARY_COLOR}, {GOLD_COLOR}); border-radius: 2px;}}
    .event-card {{
        background: #FFFFFF;
        border-left: 4px solid {GOLD_COLOR};
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 2px 3px 8px rgba(0,0,0,0.08);
    }}
    .progress-bar-container {{
        height: 28px;
        background: #e9e9e9;
        border-radius: 14px;
        overflow: hidden;
        margin: 0.5rem 0;
    }}
    .progress-bar-fill {{
        height: 100%;
        text-align: center;
        line-height: 28px;
        color: white;
        font-weight: bold;
        font-size: 0.85rem;
        border-radius: 14px;
        transition: width 0.5s ease;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔗 CALCULATE TOTAL BALANCE
# ==========================================
def get_total_contributions():
    try:
        res = supabase.table("members").select("contribution").execute()
        return sum(float(m["contribution"]) for m in res.data) if res.data else 0.0
    except:
        return 0.0

def get_transaction_net():
    try:
        res = supabase.table("transactions1").select("amount,type").execute()
        income = sum(float(r["amount"]) for r in res.data if r["type"] == "Income")
        expense = sum(float(r["amount"]) for r in res.data if r["type"] == "Expense")
        return income - expense
    except:
        return 0.0

def get_total_balance():
    return round(get_total_contributions() + get_transaction_net(), 2)

# ==========================================
# 📊 TRANSACTIONS — SIMPLIFIED ✅ NO ERRORS
# ==========================================
def add_transaction(desc, amount, trans_type):
    supabase.table("transactions1").insert({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "amount": float(amount),
        "type": trans_type
    }).execute()

def delete_transaction(row_id):
    supabase.table("transactions1").delete().eq("id", row_id).execute()

def get_history():
    res = supabase.table("transactions1").select("*").order("date", desc=True).execute()
    return res.data if res.data else []

# ==========================================
# 👥 MEMBERS
# ==========================================
def init_default_members():
    try:
        res = supabase.table("members").select("*").execute()
        if not res.data:
            default = [
                {"name": "Juan Dela Cruz", "position": "Member", "contribution": 1000.00},
                {"name": "Maria Santos", "position": "Member", "contribution": 750.00},
                {"name": "Pedro Reyes", "position": "Member", "contribution": 500.00},
                {"name": "Ana Cruz", "position": "Member", "contribution": 0.00},
            ]
            for m in default:
                supabase.table("members").insert(m).execute()
    except:
        pass

def get_all_members():
    res = supabase.table("members").select("*").order("name").execute()
    return res.data if res.data else []

def add_member(name, position, contribution):
    supabase.table("members").insert({
        "name": name, "position": position, "contribution": float(contribution)
    }).execute()

def update_member(member_id, name, position, contribution):
    supabase.table("members").update({
        "name": name, "position": position, "contribution": float(contribution)
    }).eq("id", member_id).execute()

def delete_member(member_id):
    supabase.table("members").delete().eq("id", member_id).execute()

# ==========================================
# 📅 EVENTS
# ==========================================
def get_all_events():
    res = supabase.table("events").select("*").order("event_date").execute()
    return res.data if res.data else []

def add_event(name, event_date, goal_amount, details):
    supabase.table("events").insert({
        "name": name,
        "event_date": str(event_date),
        "goal_amount": float(goal_amount),
        "details": details
    }).execute()

def update_event(event_id, name, event_date, goal_amount, details):
    supabase.table("events").update({
        "name": name,
        "event_date": str(event_date),
        "goal_amount": float(goal_amount),
        "details": details
    }).eq("id", event_id).execute()

def delete_event(event_id):
    supabase.table("events").delete().eq("id", event_id).execute()

# ==========================================
# 🔐 LOGIN SYSTEM
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "edit_member_id" not in st.session_state:
    st.session_state.edit_member_id = None
if "edit_event_id" not in st.session_state:
    st.session_state.edit_event_id = None

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>💰 SPTYO Fund Monitor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Sitio Pagkakaisa Talented Youth — Savings Tracking System</p>", unsafe_allow_html=True)
    st.markdown("<div class='rainbow-line'></div><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("🔑 Login", use_container_width=True):
            if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success("✅ Welcome!")
                st.rerun()
            else:
                st.error("❌ Invalid login")
    st.stop()

# ==========================================
# 🧭 SIDEBAR — 4 BUTTONS
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🏛️ SPTYO</h2>", unsafe_allow_html=True)
    st.markdown("<div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.info(f"Welcome, *{st.session_state.user}*!")
    st.divider()

    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.session_state.edit_member_id = None
        st.session_state.edit_event_id = None
        st.rerun()

    if st.button("👥 Member Contributions", use_container_width=True):
        st.session_state.current_page = "Contributions"
        st.session_state.edit_member_id = None
        st.session_state.edit_event_id = None
        st.rerun()

    if st.button("📅 Events & Projects", use_container_width=True):
        st.session_state.current_page = "Events"
        st.session_state.edit_member_id = None
        st.session_state.edit_event_id = None
        st.rerun()

    if st.button("📋 Transaction History", use_container_width=True):
        st.session_state.current_page = "History"
        st.session_state.edit_member_id = None
        st.session_state.edit_event_id = None
        st.rerun()

    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_page = "Dashboard"
        st.rerun()

# ==========================================
# 📊 DASHBOARD
# ==========================================
if st.session_state.current_page == "Dashboard":
    init_default_members()
    total_balance = get_total_balance()
    total_contrib = get_total_contributions()
    other_trans = get_transaction_net()

    st.markdown(f"""<div class='metric-card'>
        <h3 style='margin:0;'>💰 Total Savings Balance</h3>
        <p class='balance-text'>₱{total_balance:,.2f}</p>
    </div>""", unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.info(f"👥 Member Contributions: *₱{total_contrib:,.2f}*")
    with colB:
        st.info(f"📝 Other Transactions: *₱{other_trans:,.2f}*")

    st.divider()
    st.subheader("➕ Record New Transaction")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns([2,1])
        with col1: desc = st.text_input("📝 Description / Purpose")
        with col2: amount = st.number_input("💵 Amount (₱)", min_value=0.0, step=10.0)
        trans_type = st.radio("Transaction Type", ["💹 Income", "📤 Expense"], horizontal=True)
        submitted = st.form_submit_button("💾 Save Transaction")

    if submitted and desc and amount > 0:
        t_type = "Income" if "Income" in trans_type else "Expense"
        add_transaction(desc, amount, t_type)
        st.success("✅ Saved! Balance updated.")
        st.balloons()
        st.rerun()

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Fund Monitor System")

# ==========================================
# 👥 MEMBER CONTRIBUTIONS
# ==========================================
elif st.session_state.current_page == "Contributions":
    st.markdown("<h2>👥 Member Contributions</h2>", unsafe_allow_html=True)
    st.divider()
    init_default_members()
    members = get_all_members()
    total_contribution = get_total_contributions()

    with st.expander("➕ Add New Member"):
        with st.form("add_member_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1: name = st.text_input("Full Name")
            with col2: position = st.text_input("Position / Role", value="Member")
            with col3: contrib = st.number_input("Contribution (₱)", min_value=0.0, step=10.0)
            if st.form_submit_button("✅ Add Member") and name:
                add_member(name, position, contrib)
                st.success(f"✅ Added: {name}")
                st.balloons()
                st.rerun()

    if st.session_state.edit_member_id is not None:
        member = next((m for m in members if m["id"] == st.session_state.edit_member_id), None)
        if member:
            st.subheader("✏️ Edit Member")
            with st.form("edit_member_form"):
                col1, col2, col3 = st.columns(3)
                with col1: new_name = st.text_input("Full Name", value=member["name"])
                with col2: new_pos = st.text_input("Position / Role", value=member["position"])
                with col3: new_amt = st.number_input("Contribution (₱)", min_value=0.0, step=10.0, value=float(member["contribution"]))
                colA, colB = st.columns([1,5])
                with colA:
                    if st.form_submit_button("💾 Save"):
                        update_member(member["id"], new_name, new_pos, new_amt)
                        st.success("✅ Updated!")
                        st.session_state.edit_member_id = None
                        st.rerun()
                with colB:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.edit_member_id = None
                        st.rerun()
            st.divider()

    st.subheader("📋 Member List")
    if members:
        for m in members:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            with col1: st.markdown(f"*{m['name']}*")
            with col2: st.markdown(f"{m['position']}")
            with col3: st.markdown(f"*₱{float(m['contribution']):,.2f}*")
            with col4:
                if st.button("✏️", key=f"edit_{m['id']}"):
                    st.session_state.edit_member_id = m["id"]
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"del_{m['id']}", type="secondary"):
                    delete_member(m["id"])
                    st.success("✅ Deleted!")
                    st.rerun()
            st.markdown("---")
        st.markdown(f"### 💰 Total Contributions: *₱{total_contribution:,.2f}*")
        st.info("🔗 Linked to Dashboard Balance & Event Progress Bars.")
    else:
        st.info("📭 No members yet. Add one above!")

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Member Contributions Record")

# ==========================================
# 📅 EVENTS & PROJECTS — WITH PROGRESS BAR ✅
# ==========================================
elif st.session_state.current_page == "Events":
    st.markdown("<h2>📅 Upcoming Events & Projects</h2>", unsafe_allow_html=True)
    st.divider()

    current_balance = get_total_balance()

    with st.expander("➕ Add New Event / Project"):
        with st.form("add_event_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: event_name = st.text_input("📌 Event / Project Name")
            with col2: event_date = st.date_input("📅 Event Date")
            goal_amt = st.number_input("🎯 Fund Goal Amount (₱)", min_value=0.0, step=100.0)
            details = st.text_area("📝 Description / Details")
            if st.form_submit_button("✅ Add Event") and event_name:
                add_event(event_name, event_date, goal_amt, details)
                st.success(f"✅ Added: {event_name}")
                st.balloons()
                st.rerun()

    events = get_all_events()
    if st.session_state.edit_event_id is not None:
        evt = next((e for e in events if e["id"] == st.session_state.edit_event_id), None)
        if evt:
            st.subheader("✏️ Edit Event")
            with st.form("edit_event_form"):
                from datetime import datetime as dt
                col1, col2 = st.columns(2)
                with col1: new_name = st.text_input("Event Name", value=evt["name"])
                with col2:
                    try:
                        default_date = dt.strptime(evt["event_date"], "%Y-%m-%d")
                    except:
                        default_date = dt.now()
                    new_date = st.date_input("Event Date", value=default_date)
                new_goal = st.number_input("Goal Amount (₱)", min_value=0.0, step=100.0, value=float(evt["goal_amount"]))
                new_details = st.text_area("Details", value=evt.get("details", ""))
                colA, colB = st.columns([1,5])
                with colA:
                    if st.form_submit_button("💾 Save"):
                        update_event(evt["id"], new_name, new_date, new_goal, new_details)
                        st.success("✅ Event Updated!")
                        st.session_state.edit_event_id = None
                        st.rerun()
                with colB:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.edit_event_id = None
                        st.rerun()
            st.divider()

    st.subheader("🎯 Event Fund Goals")
    if events:
        for evt in events:
            goal = float(evt["goal_amount"])
            progress_pct = min(100.0, round((current_balance / goal * 100), 1)) if goal > 0 else 0.0

            if progress_pct >= 100:
                bar_color = GREEN_ACCENT
            elif progress_pct >= 50:
                bar_color = YELLOW_ACCENT
            else:
                bar_color = RED_ACCENT

            st.markdown(f"""
            <div class='event-card'>
                <h3 style='margin-top:0; margin-bottom:0.3rem;'>📌 {evt['name']}</h3>
                <p style='color:#555; margin:0.2rem 0;'><strong>📅 Date:</strong> {evt['event_date']}</p>
                <p style='margin:0.4rem 0;'><strong>🎯 Goal:</strong> ₱{goal:,.2f} | <strong>💰 Current Balance:</strong> ₱{current_balance:,.2f}</p>
                <div class='progress-bar-container'>
                    <div class='progress-bar-fill' style='width:{progress_pct}%; background:{bar_color};'>
                        {progress_pct}%
                    </div>
                </div>
                <p style='font-size:0.9rem; color:#666; margin-top:0.4rem;'>{evt.get('details', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            colE1, colE2, colE3 = st.columns([4, 1, 1])
            with colE2:
                if st.button("✏️ Edit", key=f"editevt_{evt['id']}"):
                    st.session_state.edit_event_id = evt["id"]
                    st.rerun()
            with colE3:
                if st.button("🗑️ Delete", key=f"delevent_{evt['id']}", type="secondary"):
                    delete_event(evt["id"])
                    st.success("✅ Event Deleted!")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No events yet. Add one above!")

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Events & Projects Tracker")

# ==========================================
# 📋 TRANSACTION HISTORY
# ==========================================
elif st.session_state.current_page == "History":
    st.markdown("<h2>📋 Transaction History</h2>", unsafe_allow_html=True)
    st.divider()
    history = get_history()

    if history:
        for row in history:
            col1, col2, col3, col4 = st.columns([4, 2, 3, 1])
            with col1:
                st.markdown(f"*{row['date']}*  \n{row['description']}")
            with col2:
                st.markdown(f"*{row['type']}*")
            with col3:
                amt = f"₱{float(row['amount']):,.2f}"
                st.markdown(f"*{amt}*")
            with col4:
                if st.button("🗑️", key=f"del_{row['id']}", type="secondary"):
                    delete_transaction(row["id"])
                    st.success("✅ Deleted!")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No transactions yet. Add one from the Dashboard!")

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Fund Monitor System")