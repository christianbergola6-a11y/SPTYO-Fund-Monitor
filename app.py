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
# 🔐 ROLE-BASED CREDENTIALS
# ==========================================
USER_ROLES = {
    "president":     {"password": "Pagkakaisa2026",  "role": "President"},
    "vicepresident": {"password": "VPSPTYO2026",     "role": "Vice President"},
    "treasurer":     {"password": "SPTYOfunds2026",  "role": "Treasurer"},
    "member":        {"password": "SPTYOmember2026", "role": "Member"},
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
        background: #FFFFFF; border-left: 4px solid {GOLD_COLOR};
        border-radius: 12px; padding: 1.2rem; margin: 0.8rem 0;
        box-shadow: 2px 3px 8px rgba(0,0,0,0.08);
    }}
    .request-card {{
        background: #FFFFFF; border-left: 4px solid; border-radius: 12px;
        padding: 1.2rem; margin: 0.8rem 0; box-shadow: 2px 3px 8px rgba(0,0,0,0.08);
    }}
    .status-pending {{border-color: {YELLOW_ACCENT};}}
    .status-approved {{border-color: {GREEN_ACCENT};}}
    .status-denied {{border-color: {RED_ACCENT};}}
    .progress-bar-container {{
        height: 28px; background: #e9e9e9; border-radius: 14px; overflow: hidden; margin: 0.5rem 0;
    }}
    .progress-bar-fill {{
        height: 100%; text-align: center; line-height: 28px; color: white;
        font-weight: bold; font-size: 0.85rem; border-radius: 14px; transition: width 0.5s ease;
    }}
    .role-badge {{
        display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px;
        font-weight: bold; font-size: 0.9rem; margin-bottom: 1rem;
    }}
    .role-president {{background: #ffd700; color: #000;}}
    .role-vp {{background: #4285F4; color: white;}}
    .role-treasurer {{background: #34A853; color: white;}}
    .role-member {{background: #9e9e9e; color: white;}}
    .voted-tag {{background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; font-weight:bold;}}
    .member-card {{
        background:#FFFFFF; padding:0.8rem; border-radius:10px;
        border-left:4px solid #34A853; margin:0.5rem 0;
        box-shadow:1px 2px 4px rgba(0,0,0,0.05);
    }}
    .member-card-vp {{border-left-color: #4285F4;}}
    .member-card-president {{border-left-color: #ffd700;}}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔗 CALCULATIONS — NOW SUMS ALL MEMBERS
# ==========================================
def get_all_members():
    """✅ Get ALL members — returns list, not just one"""
    try:
        res = supabase.table("member").select("*").order("contribution", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"❌ Failed to load members: {e}")
        return []

def get_total_contribution():
    """✅ SUM of ALL members' contributions"""
    members = get_all_members()
    return round(sum(float(m.get("contribution", 0)) for m in members), 2)

def get_transaction_net():
    try:
        res = supabase.table("transactions1").select("amount,type,status").execute()
        income = sum(float(r["amount"]) for r in res.data if r["type"] == "Income")
        expense = sum(float(r["amount"]) for r in res.data if r["type"] == "Expense" and r.get("status") == "Approved")
        return income - expense
    except: return 0.0

def get_total_balance():
    return round(get_total_contribution() + get_transaction_net(), 2)

# ==========================================
# 📊 TRANSACTIONS
# ==========================================
def add_transaction(desc, amount, trans_type):
    try:
        status = "Approved" if trans_type == "Income" else "Pending Approval"
        supabase.table("transactions1").insert({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": desc,
            "amount": float(amount),
            "type": trans_type,
            "status": status
        }).execute()
        return True
    except: return False

def get_history():
    res = supabase.table("transactions1").select("*").order("date", desc=True).execute()
    return res.data if res.data else []

# ==========================================
# 📤 EXPENSE/PROJECT REQUESTS SYSTEM
# ==========================================
def submit_request(title, purpose, amount, requested_by):
    try:
        supabase.table("requests").insert({
            "title": title,
            "purpose": purpose,
            "amount": float(amount),
            "requested_by": requested_by,
            "status": "Pending",
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }).execute()
        return True
    except: return False

def get_all_requests():
    res = supabase.table("requests").select("*").order("submitted_at", desc=True).execute()
    return res.data if res.data else []

def update_request_status(request_id, new_status):
    supabase.table("requests").update({"status": new_status, "reviewed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("id", request_id).execute()

# ==========================================
# 👤 MEMBER FUNCTIONS — ADD, EDIT, DELETE
# ==========================================
def add_member(name, position, contribution):
    """✅ ADD NEW MEMBER — does NOT replace old ones!"""
    try:
        supabase.table("member").insert({
            "name": name,
            "position": position,
            "contribution": float(contribution),
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }).execute()
        return True
    except Exception as e:
        st.error(f"❌ Failed to add: {e}")
        return False

def update_member(member_id, name, position, contribution):
    """✅ EDIT EXISTING MEMBER"""
    try:
        supabase.table("member").update({
            "name": name,
            "position": position,
            "contribution": float(contribution)
        }).eq("id", member_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Failed to update: {e}")
        return False

def delete_member(member_id):
    """✅ DELETE SELECTED MEMBER BY ID — PRESIDENT ONLY"""
    try:
        supabase.table("member").delete().eq("id", member_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete: {e}")
        return False

# ==========================================
# 📅 EVENTS — WITH DELETE FUNCTION
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

def delete_event(event_id):
    try:
        supabase.table("events").delete().eq("id", event_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete event: {e}")
        return False

# ==========================================
# 🗳️ POLLS
# ==========================================
def get_all_polls():
    res = supabase.table("polls").select("*").order("created_at", desc=True).execute()
    return res.data if res.data else []

def create_poll(question, options):
    try:
        data = {
            "question": question,
            "options": options,
            "votes": {opt: 0 for opt in options},
            "voters": {},
            "created_at": datetime.now().isoformat()
        }
        supabase.table("polls").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"❌ Failed to create poll: {e}")
        return False

def delete_poll(poll_id):
    try:
        supabase.table("polls").delete().eq("id", poll_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete: {e}")
        return False

def vote_poll(poll_id, option, username):
    try:
        res = supabase.table("polls").select("votes, voters").eq("id", poll_id).execute()
        if not res.data: return False
        data = res.data[0]
        votes = data.get("votes") or {}
        voters = data.get("voters") or {}

        if username in voters:
            old_vote = voters[username]
            votes[old_vote] = max(0, votes.get(old_vote, 1) - 1)

        votes[option] = votes.get(option, 0) + 1
        voters[username] = option

        supabase.table("polls").update({"votes": votes, "voters": voters}).eq("id", poll_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Voting failed: {e}")
        return False

# ==========================================
# 🔐 LOGIN SYSTEM
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>💰 SPTYO Fund Monitor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Sitio Pagkakaisa Talented Youth — Savings Tracking System</p>", unsafe_allow_html=True)
    st.markdown("<div class='rainbow-line'></div><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("🔑 Login", use_container_width=True):
            if username in USER_ROLES and USER_ROLES[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_role = USER_ROLES[username]["role"]
                st.success(f"✅ Welcome! Logged in as: {st.session_state.user_role}")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    st.stop()

# ==========================================
# 🧭 SIDEBAR — MANAGE MEMBERS = TREASURER ONLY
# ==========================================
role = st.session_state.user_role
username = st.session_state.username
role_class = {"President":"role-president", "Vice President":"role-vp", "Treasurer":"role-treasurer", "Member":"role-member"}.get(role, "")

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🏛️ SPTYO</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='role-badge {role_class}' style='text-align:center;'>{role}</div>", unsafe_allow_html=True)
    st.markdown("<div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.divider()

    if role == "President":
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        if st.button("📋 Transactions", use_container_width=True):
            st.session_state.current_page = "Transactions"
            st.rerun()
        if st.button("📤 Expense Requests", use_container_width=True):
            st.session_state.current_page = "Expense Requests"
            st.rerun()
        if st.button("📅 Events & Projects", use_container_width=True):
            st.session_state.current_page = "Events"
            st.rerun()
        if st.button("🗳️ Polls", use_container_width=True):
            st.session_state.current_page = "Polls"
            st.rerun()

    elif role == "Vice President":
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        if st.button("📋 Transactions", use_container_width=True):
            st.session_state.current_page = "Transactions"
            st.rerun()
        if st.button("📤 Submit Request", use_container_width=True):
            st.session_state.current_page = "Submit Request"
            st.rerun()
        if st.button("📅 Events & Projects", use_container_width=True):
            st.session_state.current_page = "Events"
            st.rerun()

    elif role == "Treasurer":
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        if st.button("➕ Record Transactions", use_container_width=True):
            st.session_state.current_page = "Record Transactions"
            st.rerun()
        if st.button("📈 Financial Reports", use_container_width=True):
            st.session_state.current_page = "Financial Reports"
            st.rerun()
        if st.button("👤 Manage Members", use_container_width=True):
            st.session_state.current_page = "Manage Members"
            st.rerun()

    elif role == "Member":
        if st.button("💰 View Balance", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        if st.button("👤 My Contribution", use_container_width=True):
            st.session_state.current_page = "My Contribution"
            st.rerun()
        if st.button("🗳️ Polls", use_container_width=True):
            st.session_state.current_page = "Polls"
            st.rerun()
        if st.button("📢 Announcements", use_container_width=True):
            st.session_state.current_page = "Announcements"
            st.rerun()

    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.current_page = "Dashboard"
        st.rerun()

# ==========================================
# 📊 DASHBOARD — SHOWS TOTAL OF ALL MEMBERS
# ==========================================
if st.session_state.current_page == "Dashboard":
    total_balance = get_total_balance()
    total_contrib = get_total_contribution()
    other_trans = get_transaction_net()

    st.markdown(f"""<div class='metric-card'>
        <h3 style='margin:0;'>💰 Total Savings Balance</h3>
        <p class='balance-text'>₱{total_balance:,.2f}</p>
    </div>""", unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA: st.info(f"👥 Total Contributions: ₱{total_contrib:,.2f}")
    with colB: st.info(f"📝 Transactions Net: ₱{other_trans:,.2f}")

    # ✅ LIST ALL MEMBERS ON DASHBOARD
    members = get_all_members()
    if members:
        st.markdown("---")
        st.subheader("👥 All Members & Contributions")
        for m in members:
            pos_class = "member-card-president" if m.get("position") == "President" else "member-card-vp" if m.get("position") == "Vice President" else ""
            st.markdown(f"""
            <div class='member-card {pos_class}'>
                <strong>{m.get('name', 'Unknown')}</strong> — {m.get('position', 'Member')}
                <span style='float:right; font-weight:bold; color:#34A853;'>₱{float(m.get('contribution', 0)):,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><div class='rainbow-line'></div>", unsafe_allow_html=True)
    st.caption(f"🏛️ SPTYO Fund Monitor — Logged in as: {role}")

# ==========================================
# 📋 TRANSACTIONS — ALL MEMBERS LIST + PRESIDENT DELETE
# ==========================================
elif st.session_state.current_page == "Transactions":
    st.markdown("<h2>📋 Complete Transaction History</h2>", unsafe_allow_html=True)
    st.divider()

    # ✅ SHOW ALL MEMBERS
    members = get_all_members()
    total_contrib = get_total_contribution()

    st.subheader("👥 All Members & Contributions")
    if members:
        for m in members:
            pos_class = "member-card-president" if m.get("position") == "President" else "member-card-vp" if m.get("position") == "Vice President" else ""

            col_info, col_del = st.columns([8, 1])
            with col_info:
                st.markdown(f"""
                <div class='member-card {pos_class}'>
                    <strong>{m.get('name', 'Unknown')}</strong> — {m.get('position', 'Member')}
                    <span style='float:right; font-weight:bold; color:#34A853;'>₱{float(m.get('contribution', 0)):,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            # ✅ DELETE BUTTON — PRESIDENT ONLY
            with col_del:
                if role == "President":
                    if st.button("🗑️", key=f"del_member_{m['id']}", help=f"Delete {m.get('name')}"):
                        if delete_member(m['id']):
                            st.success(f"✅ Deleted {m.get('name')}!")
                            st.rerun()
        st.markdown(f"### 💰 Total: *₱{total_contrib:,.2f}*")
    else:
        st.info("📭 No members added yet.")

    st.markdown("---")

    history = get_history()
    if history:
        for row in history:
            col1, col2, col3, col4 = st.columns([3, 1.5, 2, 2])
            status = row.get("status", "Approved")
            status_icon = "🟢" if status == "Approved" else "🟡" if status == "Pending Approval" else "🔴"
            with col1: st.markdown(f"{row['date']}  \n{row['description']}")
            with col2: st.markdown(f"{row['type']}")
            with col3: st.markdown(f"₱{float(row['amount']):,.2f}")
            with col4: st.markdown(f"{status_icon} {status}")
            st.markdown("---")
    else:
        st.info("📭 No transactions yet.")

# ==========================================
# 📤 EXPENSE REQUESTS — PRESIDENT
# ==========================================
elif st.session_state.current_page == "Expense Requests":
    st.markdown("<h2>📤 Expense & Project Requests — Review & Approve</h2>", unsafe_allow_html=True)
    st.divider()
    requests = get_all_requests()

    if requests:
        for req in requests:
            status = req.get("status", "Pending")
            status_class = "status-pending" if status == "Pending" else "status-approved" if status == "Approved" else "status-denied"
            status_icon = "⏳" if status == "Pending" else "✅" if status == "Approved" else "❌"

            st.markdown(f"""
            <div class='request-card {status_class}'>
                <h3 style='margin-top:0;'>{req['title']}</h3>
                <p><strong>📝 Purpose:</strong> {req['purpose']}</p>
                <p><strong>💵 Amount:</strong> ₱{float(req['amount']):,.2f}</p>
                <p><strong>👤 Requested By:</strong> {req['requested_by']} on {req['submitted_at']}</p>
                <p><strong>Status:</strong> {status_icon} <strong>{status}</strong></p>
            </div>
            """, unsafe_allow_html=True)

            if status == "Pending":
                colA, colB = st.columns(2)
                with colA:
                    if st.button("✅ APPROVE", key=f"ok_{req['id']}"):
                        update_request_status(req['id'], "Approved")
                        st.success("✅ Request APPROVED!")
                        st.rerun()
                with colB:
                    if st.button("❌ DENY", key=f"no_{req['id']}", type="secondary"):
                        update_request_status(req['id'], "Denied")
                        st.error("❌ Request DENIED!")
                        st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No requests submitted yet.")

# ==========================================
# 📤 SUBMIT REQUEST — VICE PRESIDENT
# ==========================================
elif st.session_state.current_page == "Submit Request":
    st.markdown("<h2>📤 Submit Expense / Project Request</h2>", unsafe_allow_html=True)
    st.divider()

    with st.form("request_form", clear_on_submit=True):
        title = st.text_input("📌 Request Title / Project Name")
        purpose = st.text_area("📝 Purpose / Description")
        amount = st.number_input("💵 Estimated Amount (₱)", min_value=0.0, step=100.0)
        submitted = st.form_submit_button("📤 Submit Request to President")

    if submitted and title and purpose and amount > 0:
        if submit_request(title, purpose, amount, "Vice President"):
            st.success("✅ Request SUBMITTED! Status: ⏳ Pending Approval from President")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Failed to submit! Try again.")

    st.divider()
    st.subheader("📋 My Request History")
    requests = [r for r in get_all_requests() if r.get("requested_by") == "Vice President"]
    if requests:
        for req in requests:
            status = req.get("status", "Pending")
            icon = "⏳" if status == "Pending" else "✅" if status == "Approved" else "❌"
            st.markdown(f"• {req['title']} — ₱{float(req['amount']):,.2f} — {icon}*{status}**")
    else:
        st.info("📭 No submitted requests yet.")

# ==========================================
# 👤 MANAGE MEMBERS — TREASURER ONLY (ADD + EDIT)
# ==========================================
elif st.session_state.current_page == "Manage Members":
    st.markdown("<h2>👤 Manage Members & Contributions</h2>", unsafe_allow_html=True)
    st.divider()

    # ✅ ADD NEW MEMBER FORM
    st.subheader("➕ Add New Member")
    with st.form("add_member_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1: name = st.text_input("Full Name")
        with col2: position = st.text_input("Position / Role")
        contribution = st.number_input("Contribution Amount (₱)", min_value=0.0, step=10.0)
        if st.form_submit_button("💾 Add Member") and name.strip():
            if add_member(name.strip(), position.strip() or "Member", contribution):
                st.success(f"✅ {name} added! Previous members still saved!")
                st.balloons()
                st.rerun()

    st.markdown("---")

    # ✅ EDIT EXISTING MEMBERS
    st.subheader("✏️ Edit Existing Members")
    members = get_all_members()
    if not members:
        st.info("📭 No members yet. Add one above!")
    else:
        for m in members:
            with st.expander(f"📝 {m.get('name')} — {m.get('position')}"):
                with st.form(f"edit_{m['id']}"):
                    e_name = st.text_input("Name", value=m.get("name", ""))
                    e_pos = st.text_input("Position", value=m.get("position", ""))
                    e_amt = st.number_input("Contribution", min_value=0.0, step=10.0, value=float(m.get("contribution", 0)))
                    if st.form_submit_button("✅ Update"):
                        if update_member(m['id'], e_name.strip(), e_pos.strip(), e_amt):
                            st.success(f"✅ Updated {e_name}!")
                            st.rerun()

# ==========================================
# ➕ RECORD TRANSACTIONS — TREASURER
# ==========================================
elif st.session_state.current_page == "Record Transactions":
    st.markdown("<h2>➕ Record Income & Expenses</h2>", unsafe_allow_html=True)
    st.divider()

    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns([2,1])
        with col1: desc = st.text_input("📝 Description / Purpose")
        with col2: amount = st.number_input("💵 Amount (₱)", min_value=0.0, step=10.0)
        trans_type = st.radio("Transaction Type", ["💹 Income", "📤 Expense"], horizontal=True)
        submitted = st.form_submit_button("💾 Save Transaction")

    if submitted and desc and amount > 0:
        t_type = "Income" if "Income" in trans_type else "Expense"
        if add_transaction(desc, amount, t_type):
            if t_type == "Income":
                st.success("✅ Income Recorded!")
            else:
                st.info("⏳ Expense Saved — Pending Approval from President/VP")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Failed to save! Check Supabase setup.")

    st.divider()
    st.subheader("📋 Recent Transactions")
    history = get_history()[:5] if get_history() else []
    for row in history:
        status = row.get("status", "Approved")
        st.markdown(f"• {row['date']} — {row['description']} — ₱{float(row['amount']):,.2f} —*{status}**")

# ==========================================
# 📈 FINANCIAL REPORTS — TREASURER
# ==========================================
elif st.session_state.current_page == "Financial Reports":
    st.markdown("<h2>📈 Financial Reports</h2>", unsafe_allow_html=True)
    st.divider()

    total_balance = get_total_balance()
    total_contrib = get_total_contribution()
    history = get_history()
    income = sum(float(r["amount"]) for r in history if r["type"] == "Income")
    expense = sum(float(r["amount"]) for r in history if r["type"] == "Expense" and r.get("status") == "Approved")
    pending = sum(float(r["amount"]) for r in history if r.get("status") == "Pending Approval")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("💰 Total Balance", f"₱{total_balance:,.2f}")
    with col2: st.metric("💹 Total Income", f"₱{income:,.2f}")
    with col3: st.metric("📤 Approved Expenses", f"₱{expense:,.2f}")
    with col4: st.metric("⏳ Pending Approval", f"₱{pending:,.2f}")

    st.divider()
    st.subheader("👥 All Members")
    members = get_all_members()
    if members:
        for m in members:
            st.markdown(f"• *{m.get('name')}* — {m.get('position')} — ₱{float(m.get('contribution', 0)):,.2f}")
    st.markdown(f"### 💰 Total Contributions:*₱{total_contrib:,.2f}**")

# ==========================================
# 👤 MY CONTRIBUTION — MEMBER
# ==========================================
elif st.session_state.current_page == "My Contribution":
    st.markdown("<h2>👤 My Contribution</h2>", unsafe_allow_html=True)
    st.divider()
    members = get_all_members()

    if not members:
        st.info("ℹ️ No members recorded yet. Ask Treasurer to add you!")
    else:
        for m in members:
            st.markdown(f"""
            <div class='member-card'>
                <h4 style='margin:0;'>{m.get('name', 'Unknown')}</h4>
                <p style='margin:0.2rem 0;'>{m.get('position', 'Member')}</p>
                <p style='font-size:1.3rem; font-weight:bold; color:#34A853; margin:0;'>₱{float(m.get('contribution', 0)):,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"### 💰 Total: *₱{get_total_contribution():,.2f}*")

# ==========================================
# 📅 EVENTS
# ==========================================
elif st.session_state.current_page == "Events":
    st.markdown("<h2>📅 Events & Projects</h2>", unsafe_allow_html=True)
    st.divider()
    current_balance = get_total_balance()

    if role in ["President", "Vice President"]:
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
                    st.rerun()

    events = get_all_events()
    st.subheader("🎯 Event Fund Goals")
    if events:
        for evt in events:
            goal = float(evt["goal_amount"])
            progress_pct = min(100.0, round((current_balance / goal * 100), 1)) if goal > 0 else 0.0
            bar_color = GREEN_ACCENT if progress_pct >= 100 else YELLOW_ACCENT if progress_pct >= 50 else RED_ACCENT

            col_info, col_del = st.columns([9, 1])
            with col_info:
                st.markdown(f"""
                <div class='event-card'>
                    <h3 style='margin-top:0; margin-bottom:0.3rem;'>📌 {evt['name']}</h3>
                    <p style='color:#555; margin:0.2rem 0;'><strong>📅 Date:</strong> {evt['event_date']}</p>
                    <p style='margin:0.4rem 0;'><strong>🎯 Goal:</strong> ₱{goal:,.2f} | <strong>💰 Current Balance:</strong> ₱{current_balance:,.2f}</p>
                    <div class='progress-bar-container'>
                        <div class='progress-bar-fill' style='width:{progress_pct}%; background:{bar_color};'>{progress_pct}%</div>
                    </div>
                    <p style='font-size:0.9rem; color:#666; margin-top:0.4rem;'>{evt.get('details', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if role == "President":
                    if st.button("🗑️", key=f"del_evt_{evt['id']}", help="Delete this event"):
                        if delete_event(evt["id"]):
                            st.success("✅ Event deleted!")
                            st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No events yet.")

# ==========================================
# 🗳️ POLLS
# ==========================================
elif st.session_state.current_page == "Polls":
    st.markdown("<h2>🗳️ Polls & Voting</h2>", unsafe_allow_html=True)
    st.divider()

    if role == "President":
        with st.expander("➕ Create New Poll"):
            with st.form("poll_form", clear_on_submit=True):
                question = st.text_input("❓ Poll Question")
                opt1 = st.text_input("Option 1")
                opt2 = st.text_input("Option 2")
                opt3 = st.text_input("Option 3 (optional)")
                opt4 = st.text_input("Option 4 (optional)")
                if st.form_submit_button("✅ Create Poll") and question and opt1 and opt2:
                    options = [o.strip() for o in [opt1, opt2, opt3, opt4] if o.strip()]
                    if create_poll(question, options):
                        st.success("✅ Poll Created!")
                        st.rerun()

    polls = get_all_polls()
    if polls:
        for idx, p in enumerate(polls):
            poll_id = p.get("id")
            question = p.get("question", "No question")
            options = p.get("options", []) or []
            votes = p.get("votes", {}) or {}
            voters = p.get("voters", {}) or {}
            my_vote = voters.get(username, None)

            col_q, col_del = st.columns([9, 1])
            with col_q:
                st.subheader(f"❓ {question}")
                if my_vote:
                    st.markdown(f"<span class='voted-tag'>✅ You voted: {my_vote}</span>", unsafe_allow_html=True)
            with col_del:
                if role == "President":
                    if st.button("🗑️", key=f"del_poll_{poll_id}_{idx}", help="Delete this poll"):
                        if delete_poll(poll_id):
                            st.success("✅ Poll deleted!")
                            st.rerun()

            total_votes = sum(votes.values())
            for opt in options:
                count = votes.get(opt, 0)
                pct = round(count / total_votes * 100, 1) if total_votes > 0 else 0.0
                colA, colB = st.columns([4, 1])
                is_my_choice = (my_vote == opt)
                btn_label = f"✅ {opt}" if is_my_choice else f"🗳️ {opt}"

                with colA:
                    if st.button(f"{btn_label} ({count} votes — {pct}%)", key=f"vote_{poll_id}_{opt}"):
                        if vote_poll(poll_id, opt, username):
                            st.success(f"✅ Vote recorded! You voted for '{opt}'")
                            st.rerun()
                with colB:
                    st.markdown(f"**{pct}%**")
            st.markdown("---")
    else:
        st.info("📭 No polls yet.")

# ==========================================
# 📢 ANNOUNCEMENTS — MEMBER PAGE
# ==========================================
elif st.session_state.current_page == "Announcements":
    st.markdown("<h2>📢 Announcements</h2>", unsafe_allow_html=True)
    st.divider()
    st.info("📢 Announcements will appear here. Coming soon!")