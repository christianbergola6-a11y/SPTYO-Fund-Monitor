import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# ==========================================
# 🎨 SPTYO LOGO COLORS
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
# 🔑 YOUR DATABASE KEYS HERE
# ==========================================
SUPABASE_URL = "https://rfyonjupxgficvqjolph.supabase.co"   # ← YOUR URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJmeW9uanVweGdmaWN2cWpvbHBoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY1MDEzODgsImV4cCI6MjEwMjA3NzM4OH0.XTrHlteEeHoBaZ_HAvExDdGqwDHRjY0ubMmswz4MqQ8"                     # ← YOUR KEY

# ==========================================
# 🔐 LOGIN CREDENTIALS
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
# 🎨 PAGE STYLING
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
    .stButton>button[kind="primary"] {{
        background: linear-gradient(90deg, {GREEN_ACCENT}, #66bb6a);
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 DATABASE FUNCTIONS — TRANSACTIONS
# ==========================================
def recalculate_balance():
    res = supabase.table("transactions1").select("amount,type").order("date").execute()
    balance = 0.0
    for r in res.data:
        if r["type"] == "Income":
            balance += float(r["amount"])
        else:
            balance -= float(r["amount"])
    return round(balance, 2)

def add_transaction(desc, amount, trans_type):
    balance = recalculate_balance()
    new_balance = balance + amount if trans_type == "Income" else balance - amount
    supabase.table("transactions1").insert({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "amount": float(amount),
        "type": trans_type,
        "running_balance": round(new_balance, 2)
    }).execute()
    return round(new_balance, 2)

def delete_transaction(row_id):
    supabase.table("transactions1").delete().eq("id", row_id).execute()
    res = supabase.table("transactions1").select("id,amount,type").order("date").execute()
    balance = 0.0
    for row in res.data:
        if row["type"] == "Income":
            balance += float(row["amount"])
        else:
            balance -= float(row["amount"])
        supabase.table("transactions1").update({"running_balance": round(balance, 2)}).eq("id", row["id"]).execute()
    return round(balance, 2)

def get_history():
    res = supabase.table("transactions1").select("*").order("date", desc=True).execute()
    return res.data if res.data else []

# ==========================================
# 👥 MEMBER DATABASE FUNCTIONS
# ==========================================
def init_default_members():
    """Add default members if table is empty"""
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

def get_all_members():
    res = supabase.table("members").select("*").order("name").execute()
    return res.data if res.data else []

def add_member(name, position, contribution):
    supabase.table("members").insert({
        "name": name,
        "position": position,
        "contribution": float(contribution)
    }).execute()

def update_member(member_id, name, position, contribution):
    supabase.table("members").update({
        "name": name,
        "position": position,
        "contribution": float(contribution)
    }).eq("id", member_id).execute()

def delete_member(member_id):
    supabase.table("members").delete().eq("id", member_id).execute()

# ==========================================
# 🔐 LOGIN SYSTEM
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "edit_member_id" not in st.session_state:
    st.session_state.edit_member_id = None

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
# 🧭 SIDEBAR — NAVIGATION BUTTONS
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🏛️ SPTYO</h2>", unsafe_allow_html=True)
    st.markdown("<div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.info(f"Welcome, *{st.session_state.user}*!")
    st.divider()

    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.session_state.edit_member_id = None
        st.rerun()

    if st.button("👥 Member Contributions", use_container_width=True):
        st.session_state.current_page = "Contributions"
        st.session_state.edit_member_id = None
        st.rerun()

    if st.button("📋 Transaction History", use_container_width=True):
        st.session_state.current_page = "History"
        st.session_state.edit_member_id = None
        st.rerun()

    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_page = "Dashboard"
        st.session_state.edit_member_id = None
        st.rerun()

# ==========================================
# 📊 PAGE 1 — DASHBOARD
# ==========================================
if st.session_state.current_page == "Dashboard":
    balance = recalculate_balance()

    st.markdown(f"""<div class='metric-card'>
        <h3 style='margin:0;'>💰 Total Savings Balance</h3>
        <p class='balance-text'>₱{balance:,.2f}</p>
    </div><br>""", unsafe_allow_html=True)

    st.subheader("➕ Record New Transaction")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns([2,1])
        with col1: desc = st.text_input("📝 Description / Purpose")
        with col2: amount = st.number_input("💵 Amount (₱)", min_value=0.0, step=10.0)
        trans_type = st.radio("Transaction Type", ["💹 Income", "📤 Expense"], horizontal=True)
        submitted = st.form_submit_button("💾 Save Transaction")

    if submitted and desc and amount > 0:
        t_type = "Income" if "Income" in trans_type else "Expense"
        new_balance = add_transaction(desc, amount, t_type)
        st.success(f"✅ Saved! New Balance: *₱{new_balance:,.2f}*")
        st.balloons()
        st.rerun()

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Fund Monitor System")

# ==========================================
# 👥 PAGE 2 — MEMBER CONTRIBUTIONS (EDITABLE!)
# ==========================================
elif st.session_state.current_page == "Contributions":
    st.markdown("<h2>👥 Member Contributions</h2>", unsafe_allow_html=True)
    st.divider()

    # Initialize default members first time
    try:
        init_default_members()
    except:
        pass

    members = get_all_members()
    total_contribution = sum(m["contribution"] for m in members) if members else 0.0

    # ✅ ADD NEW MEMBER FORM
    with st.expander("➕ Add New Member"):
        with st.form("add_member_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1: name = st.text_input("Full Name")
            with col2: position = st.text_input("Position / Role", value="Member")
            with col3: contrib = st.number_input("Contribution (₱)", min_value=0.0, step=10.0)
            if st.form_submit_button("✅ Add Member") and name:
                add_member(name, position, contrib)
                st.success(f"✅ Added: {name}")
                st.rerun()

    # ✅ EDIT EXISTING MEMBER FORM
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

    # ✅ DISPLAY ALL MEMBERS with EDIT & DELETE buttons
    st.subheader("📋 Member List")
    if members:
        for m in members:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            with col1: st.markdown(f"*{m['name']}*")
            with col2: st.markdown(f"{m['position']}")
            with col3: st.markdown(f"*₱{float(m['contribution']):,.2f}*")
            with col4:
                if st.button("✏️", key=f"edit_{m['id']}", help="Edit this member"):
                    st.session_state.edit_member_id = m["id"]
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"del_{m['id']}", help="Delete this member", type="secondary"):
                    delete_member(m["id"])
                    st.success("✅ Deleted!")
                    st.rerun()
            st.markdown("---")

        st.markdown(f"### 💰 Total Contributions: *₱{total_contribution:,.2f}*")
    else:
        st.info("📭 No members yet. Add one above!")

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Member Contributions Record")

# ==========================================
# 📋 PAGE 3 — TRANSACTION HISTORY
# ==========================================
elif st.session_state.current_page == "History":
    st.markdown("<h2>📋 Complete Transaction History</h2>", unsafe_allow_html=True)
    st.divider()

    history = get_history()

    if history:
        for row in history:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            with col1:
                st.markdown(f"*{row['date']}*  \n{row['description']}")
            with col2:
                st.markdown(f"*{row['type']}*")
            with col3:
                amt = f"₱{float(row['amount']):,.2f}"
                st.markdown(f"*{amt}*")
            with col4:
                bal = f"₱{float(row['running_balance']):,.2f}"
                st.markdown(f"{bal}")
            with col5:
                if st.button("🗑️", key=f"del_{row['id']}", help="Delete this transaction", type="secondary"):
                    delete_transaction(row["id"])
                    st.success("✅ Deleted! Balance recalculated.")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No transactions yet. Add one from the Dashboard page!")

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Fund Monitor System")