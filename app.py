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
SUPABASE_URL = "https://YOUR-PROJECT-ID.supabase.co"   # ← YOUR URL
SUPABASE_KEY = "YOUR-ANON-KEY-HERE"                     # ← YOUR KEY

# ==========================================
# 🔐 LOGIN CREDENTIALS
# ==========================================
ALLOWED_USERS = {
    "treasurer": "SPTYOfunds2026",
    "president": "Pagkakaisa2026"
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
# 🔗 LINKED BALANCE = CONTRIBUTIONS + OTHER TRANSACTIONS
# ==========================================
def get_total_contributions():
    """Sum of ALL member contributions"""
    try:
        res = supabase.table("members").select("contribution").execute()
        return sum(float(m["contribution"]) for m in res.data) if res.data else 0.0
    except:
        return 0.0

def get_transaction_net():
    """Net from separate transactions (Income − Expense)"""
    try:
        res = supabase.table("transactions1").select("amount,type").execute()
        income = sum(float(r["amount"]) for r in res.data if r["type"] == "Income")
        expense = sum(float(r["amount"]) for r in res.data if r["type"] == "Expense")
        return income - expense
    except:
        return 0.0

def get_dashboard_balance():
    """✅ TOTAL BALANCE = Member Contributions + Other Transactions"""
    return round(get_total_contributions() + get_transaction_net(), 2)

# ==========================================
# 📊 TRANSACTION FUNCTIONS
# ==========================================
def add_transaction(desc, amount, trans_type):
    supabase.table("transactions1").insert({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "amount": float(amount),
        "type": trans_type,
        "running_balance": 0
    }).execute()

def delete_transaction(row_id):
    supabase.table("transactions1").delete().eq("id", row_id).execute()

def get_history():
    res = supabase.table("transactions1").select("*").order("date", desc=True).execute()
    return res.data if res.data else []

# ==========================================
# 👥 MEMBER FUNCTIONS
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
# 🧭 SIDEBAR
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
# 📊 DASHBOARD — BALANCE AUTO-UPDATES!
# ==========================================
if st.session_state.current_page == "Dashboard":
    init_default_members()

    total_contrib = get_total_contributions()
    other_trans = get_transaction_net()
    total_balance = get_dashboard_balance()

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

    st.subheader("➕ Record Other Transaction")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns([2,1])
        with col1: desc = st.text_input("📝 Description / Purpose")
        with col2: amount = st.number_input("💵 Amount (₱)", min_value=0.0, step=10.0)
        trans_type = st.radio("Transaction Type", ["💹 Income", "📤 Expense"], horizontal=True)
        submitted = st.form_submit_button("💾 Save Transaction")

    if submitted and desc and amount > 0:
        t_type = "Income" if "Income" in trans_type else "Expense"
        add_transaction(desc, amount, t_type)
        st.success("✅ Saved! Dashboard balance updated.")
        st.balloons()
        st.rerun()

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Fund Monitor System")

# ==========================================
# 👥 MEMBER CONTRIBUTIONS — EDITS UPDATE BALANCE
# ==========================================
elif st.session_state.current_page == "Contributions":
    st.markdown("<h2>👥 Member Contributions</h2>", unsafe_allow_html=True)
    st.divider()

    init_default_members()
    members = get_all_members()
    total_contribution = get_total_contributions()

    # ADD NEW MEMBER
    with st.expander("➕ Add New Member"):
        with st.form("add_member_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1: name = st.text_input("Full Name")
            with col2: position = st.text_input("Position / Role", value="Member")
            with col3: contrib = st.number_input("Contribution (₱)", min_value=0.0, step=10.0)
            if st.form_submit_button("✅ Add Member") and name:
                add_member(name, position, contrib)
                st.success(f"✅ Added: {name} — Dashboard balance updated!")
                st.balloons()
                st.rerun()

    # EDIT MEMBER
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
                        st.success("✅ Updated! Dashboard balance refreshed.")
                        st.session_state.edit_member_id = None
                        st.rerun()
                with colB:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.edit_member_id = None
                        st.rerun()
            st.divider()

    # MEMBER LIST
    st.subheader("📋 Member List")
    if members:
        for m in members:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            with col1: st.markdown(f"*{m['name']}*")
            with col2: st.markdown(f"{m['position']}")
            with col3: st.markdown(f"*₱{float(m['contribution']):,.2f}*")
            with col4:
                if st.button("✏️", key=f"edit_{m['id']}", help="Edit — updates Dashboard balance"):
                    st.session_state.edit_member_id = m["id"]
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"del_{m['id']}", help="Delete — updates Dashboard balance", type="secondary"):
                    delete_member(m["id"])
                    st.success("✅ Deleted! Dashboard balance updated.")
                    st.rerun()
            st.markdown("---")

        st.markdown(f"### 💰 Total Contributions: *₱{total_contribution:,.2f}*")
        st.info("🔗 This amount is automatically added to your Dashboard Total Balance.")
    else:
        st.info("📭 No members yet. Add one above!")

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Member Contributions Record")

# ==========================================
# 📋 TRANSACTION HISTORY
# ==========================================
elif st.session_state.current_page == "History":
    st.markdown("<h2>📋 Complete Transaction History</h2>", unsafe_allow_html=True)
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
                if st.button("🗑️", key=f"del_{row['id']}", help="Delete", type="secondary"):
                    delete_transaction(row["id"])
                    st.success("✅ Deleted! Dashboard balance updated.")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No transactions yet. Add one from the Dashboard page!")

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Fund Monitor System")