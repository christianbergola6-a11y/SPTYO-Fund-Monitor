import json
import os
import shutil
from datetime import datetime
import streamlit as st

# ==========================================
# 🎨 SPTYO LOGO COLORS — MATCHED PERFECTLY!
# ==========================================
PRIMARY_COLOR = "#1A1A1A"     # Deep Black (logo ring)
GOLD_COLOR    = "#D4AF37"     # Gold accent (logo border)
CREAM_COLOR   = "#F8F4E9"     # Warm cream background
GREEN_ACCENT  = "#34A853"     # Rainbow green
RED_ACCENT    = "#EA4335"     # Rainbow red
YELLOW_ACCENT = "#FBBC05"     # Rainbow yellow
BLUE_ACCENT   = "#4285F4"     # Rainbow blue
TEXT_COLOR    = "#2C2C2C"     # Dark readable text

# ==========================================
# ⚙️ SETTINGS
# ==========================================
DATA_FILE = "fund_data.json"
BACKUP_FOLDER = "backups"
ALLOWED_USERS = {
    "president": "SPTYOfunds2026",   # ✅ Change these!
    "vicepresident": "SPTYOfunds2026"
}

os.makedirs(BACKUP_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="SPTYO Fund Monitor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 CUSTOM STYLING — MATCHES YOUR LOGO VIBE
# ==========================================
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {CREAM_COLOR};
        color: {TEXT_COLOR};
    }}
    h1, h2, h3 {{
        color: {PRIMARY_COLOR};
        font-weight: 700;
    }}
    .stButton>button {{
        background: linear-gradient(90deg, {GOLD_COLOR}, {YELLOW_ACCENT});
        color: {PRIMARY_COLOR};
        border-radius: 12px;
        border: 2px solid {PRIMARY_COLOR};
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        box-shadow: 2px 3px 0px {PRIMARY_COLOR}40;
        transition: all 0.2s ease;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 3px 5px 0px {PRIMARY_COLOR}50;
    }}
    .metric-card {{
        background: linear-gradient(135deg, #FFFFFF, {CREAM_COLOR});
        border: 3px solid {GOLD_COLOR};
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 4px 6px 0px {PRIMARY_COLOR}25;
        text-align: center;
    }}
    .balance-text {{
        font-size: 2.5rem;
        font-weight: 900;
        color: {PRIMARY_COLOR};
    }}
    .rainbow-line {{
        height: 6px;
        border-radius: 3px;
        background: linear-gradient(90deg, {RED_ACCENT}, {YELLOW_ACCENT}, {GREEN_ACCENT}, {BLUE_ACCENT});
    }}
    hr {{
        border: none;
        height: 3px;
        background: linear-gradient(90deg, {GOLD_COLOR}, {PRIMARY_COLOR}, {GOLD_COLOR});
        border-radius: 2px;
    }}
    .stTextInput>div>div>input, .stNumberInput>div>div>input {{
        border-radius: 8px;
        border: 2px solid {GOLD_COLOR};
    }}
    .css-1d391kg {{
        background-color: #EDE6D6;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📂 DATA & BACKUP FUNCTIONS
# ==========================================
def auto_backup():
    if not os.path.exists(DATA_FILE): return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_FOLDER, f"fund_backup_{timestamp}.json")
    shutil.copy2(DATA_FILE, backup_path)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"balance": 0.0, "transactions": []}

def save_data(data):
    auto_backup()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==========================================
# 🔑 LOGIN SYSTEM
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>💰 SPTYO Fund Monitor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem;'>Sitio Pagkakaisa Talented Youth — Savings Tracking System</p>", unsafe_allow_html=True)
    st.markdown("<div class='rainbow-line'></div><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Login Required")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("🔑 Login", use_container_width=True):
            if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success("✅ Welcome! Login successful.")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    st.stop()

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================
data = load_data()

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏛️ SPTYO</h2>", unsafe_allow_html=True)
    st.markdown("<div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.info(f"Welcome, *{st.session_state.user}*!")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    st.caption("🔒 Auto-backup enabled on every save")

# Balance Display — STUNNING!
st.markdown("""<div class='metric-card'>
    <h3 style='margin:0;'>💰 Total Savings Balance</h3>
    <p class='balance-text'>₱{:,.2f}</p>
</div>""".format(data['balance']), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ➕ ADD TRANSACTION FORM
# ==========================================
st.subheader("➕ Record New Transaction")
with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        desc = st.text_input("📝 Description / Purpose")
    with col2:
        amount = st.number_input("💵 Amount (₱)", min_value=0.0, step=10.0)
    
    trans_type = st.radio("Transaction Type", ["💹 Income", "📤 Expense"], horizontal=True)
    submitted = st.form_submit_button("💾 Save Transaction")

if submitted and desc and amount > 0:
    is_income = "Income" in trans_type
    if is_income:
        data["balance"] += amount
    else:
        data["balance"] -= amount

    data["transactions"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "amount": amount,
        "type": "Income" if is_income else "Expense",
        "running_balance": round(data["balance"], 2)
    })
    save_data(data)
    st.success(f"✅ Saved! New Balance: *₱{data['balance']:,.2f}*")
    st.balloons()
    st.rerun()

st.divider()

# ==========================================
# 📋 TRANSACTION HISTORY
# ==========================================
st.subheader("📋 Transaction History")
if data["transactions"]:
    st.table(reversed(data["transactions"]))
else:
    st.info("📭 No transactions yet. Record your first entry above!")

st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
st.caption("🏛️ Sitio Pagkakaisa Talented Youth — Fund Monitor System")