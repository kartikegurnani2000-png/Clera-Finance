import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import datetime
import json
import time
import pdfplumber
from google import genai
from google.api_core.exceptions import ResourceExhausted

# --- API KEY CONFIGURATION ---
# --- API KEY CONFIGURATION ---
try:
    DEFAULT_GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    DEFAULT_GEMINI_KEY = ""

st.set_page_config(page_title="Clera Finance UI", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS & THEMING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    :root, .stApp { color-scheme: light; }
    h1, h2, h3, h4, h5, h6, p, .stMarkdown { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp, [data-testid="stHeader"] { background-color: #F8FAFC !important; }
    [data-testid="stAppViewContainer"] { position: relative; }

    [data-testid="stAppViewContainer"]::before,
    [data-testid="stAppViewContainer"]::after {
        content: ""; position: fixed; border-radius: 50%; filter: blur(90px);
        z-index: 0; pointer-events: none;
    }
    [data-testid="stAppViewContainer"]::before {
        width: 480px; height: 480px; top: -180px; left: -160px;
        background: radial-gradient(circle, rgba(79,70,229,0.16) 0%, rgba(79,70,229,0) 70%);
    }
    [data-testid="stAppViewContainer"]::after {
        width: 520px; height: 520px; bottom: -220px; right: -180px;
        background: radial-gradient(circle, rgba(236,72,153,0.15) 0%, rgba(236,72,153,0) 70%);
    }
    [data-testid="stAppViewContainer"] .block-container { position: relative; z-index: 1; }

    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1E1B4B 0%, #312E81 55%, #4C1D95 100%) !important; }
    [data-testid="stSidebar"] * { color: #E0E7FF !important; }
    [data-testid="stSidebar"] .gradient-text { background: linear-gradient(90deg, #A5B4FC 0%, #F0ABFC 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    [data-testid="stSidebar"] [role="radiogroup"] label { border-radius: 10px; padding: 4px 10px; transition: background 0.15s ease; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,0.08); }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
    [data-testid="stSidebar"] button { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.15) !important; }

    .gradient-text { background: linear-gradient(90deg, #4F46E5 0%, #EC4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    .section-title { font-size: 1.5rem; font-weight: 800; color: #1E293B; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px; margin-top: 10px;}

    .hero-banner { background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 55%, #EC4899 100%); border-radius: 18px; padding: 30px; color: white; margin-bottom: 30px; box-shadow: 0 12px 24px -6px rgba(79,70,229,0.35); display: flex; align-items: center; gap: 20px; position: relative; overflow: hidden; }
    .hero-banner::after { content: ""; position: absolute; inset: 0; background-image: radial-gradient(circle at 85% 20%, rgba(255,255,255,0.20) 0, transparent 40%), radial-gradient(circle at 15% 90%, rgba(255,255,255,0.14) 0, transparent 35%); }

    .saas-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); position: relative; margin-bottom: 1rem; overflow: hidden; transition: transform 0.18s ease, box-shadow 0.18s ease; }
    .saas-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #4F46E5, #EC4899); opacity: 0.9; }
    .saas-card:hover { transform: translateY(-3px); box-shadow: 0 14px 22px -8px rgba(79,70,229,0.25); }
    .card-icon { position: absolute; top: 20px; right: 20px; width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .icon-green { background: #DCFCE7; color: #16A34A; }
    .icon-red { background: #FEE2E2; color: #DC2626; }
    .icon-blue { background: #DBEAFE; color: #2563EB; }
    .icon-purple { background: #F3E8FF; color: #9333EA; }
    .metric-label { color: #64748B; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em;}
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.9rem; font-weight: 700; color: #0F172A; }

    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px !important; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

    .status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px; font-weight: 700; font-size: 0.78rem; }
    .status-pill::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
    .status-paid { background: #DCFCE7; color: #16A34A; }
    .status-pending { background: #FEF3C7; color: #D97706; }
    .status-overdue { background: #FEE2E2; color: #DC2626; }

    .stButton > button[kind="primary"] { background: linear-gradient(90deg, #4F46E5, #7C3AED); border: none; box-shadow: 0 4px 10px -2px rgba(79,70,229,0.4); }
    .stButton > button[kind="primary"]:hover { box-shadow: 0 6px 14px -2px rgba(79,70,229,0.5); }
    </style>
""", unsafe_allow_html=True)

def rich_card(title, value, icon, theme):
    return f'<div class="saas-card"><div class="card-icon {theme}">{icon}</div><div class="metric-label">{title}</div><div class="metric-value">{value}</div></div>'

RETRYABLE_CODES = {429, 500, 502, 503, 504}
FALLBACK_MODELS = ['gemini-2.5-flash']

def parse_document_with_retry(models_client, model_name, contents, max_retries=5):
    # The google-genai SDK raises google.genai.errors.ServerError / ClientError
    # (with a .code attribute such as 503 or 429), NOT google.api_core's
    # ResourceExhausted, so we check the status code instead.
    models_to_try = [model_name] + [m for m in FALLBACK_MODELS if m != model_name]
    last_error = None
    for current_model in models_to_try:
        delay = 2
        for attempt in range(max_retries):
            try:
                return models_client.generate_content(model=current_model, contents=contents)
            except Exception as e:
                code = getattr(e, 'code', None)
                retryable = isinstance(e, ResourceExhausted) or code in RETRYABLE_CODES
                if not retryable:
                    if current_model == model_name:
                        raise
                    break  # fallback model failed for another reason; report original error
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
    raise last_error

# --- USER AUTHENTICATION ---
USERS_FILE = 'users.csv'
if not os.path.exists(USERS_FILE):
    pd.DataFrame([['admin', 'admin321', 'admin']], columns=['username', 'password', 'role']).to_csv(USERS_FILE, index=False)
users_df = pd.read_csv(USERS_FILE)

if 'role' not in users_df.columns:
    users_df['role'] = users_df['username'].apply(lambda u: 'admin' if str(u).strip().lower() == 'admin' else 'user')
    users_df.to_csv(USERS_FILE, index=False)

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': '', 'role': ''})

if not st.session_state['logged_in']:
    st.markdown("<br><br><h1 style='text-align: center;' class='gradient-text'>Clera Finance</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])
            with tab1:
                with st.form("login"):
                    u = st.text_input("Workspace ID").strip().lower()
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("Access Dashboard", type="primary"):
                        match = users_df[(users_df['username'] == u) & (users_df['password'] == p)]
                        if not match.empty:
                            role = match.iloc[0]['role']
                            st.session_state.update({'logged_in': True, 'username': u, 'role': role}); st.rerun()
                        else: st.error("Invalid credentials.")
            with tab2:
                with st.form("register"):
                    new_u = st.text_input("New Workspace ID").strip().lower()
                    new_p = st.text_input("New Password", type="password")
                    if st.form_submit_button("Deploy Account"):
                        if new_u in users_df['username'].values: st.error("ID exists.")
                        else:
                            pd.DataFrame([[new_u, new_p, 'user']], columns=['username', 'password', 'role']).to_csv(USERS_FILE, mode='a', header=False, index=False)
                            st.success("Deployed successfully. Please sign in.")
    st.stop()

# --- DATA MANAGEMENT ---
active_user = st.session_state['username']
USER_CSV = f"expenses_{active_user}.csv"
INCOME_CSV = f"income_{active_user}.csv"
AP_CSV = f"ap_{active_user}.csv"
HISTORY_CSV = f"history_{active_user}.csv"

@st.cache_data 
def load_data(filename, cols):
    if not os.path.exists(filename):
        pd.DataFrame(columns=cols).to_csv(filename, index=False)
    try:
        df = pd.read_csv(filename)
    except pd.errors.ParserError:
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = filename.replace('.csv', f'_corrupted_{stamp}.csv')
        os.rename(filename, backup_name)
        st.warning(f"⚠️ '{filename}' was corrupted. Backed up to '{backup_name}'.")
        df = pd.DataFrame(columns=cols)
        df.to_csv(filename, index=False)
    for col in cols:
        if col not in df.columns:
            df[col] = None
    df = df[cols]
    for date_col in ['date', 'invoice_date', 'due_date', 'timestamp']:
        if date_col in df.columns: df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    if 'amount' in df.columns: df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    return df

def migrate_ap_schema(path):
    if not os.path.exists(path): return
    try: df = pd.read_csv(path)
    except Exception: return
    changed = False
    if 'amount_paid' not in df.columns:
        df['amount_paid'] = 0.0
        changed = True
    if 'amount_remaining' not in df.columns:
        base_amount = pd.to_numeric(df.get('amount', 0), errors='coerce').fillna(0)
        df['amount_remaining'] = base_amount - pd.to_numeric(df['amount_paid'], errors='coerce').fillna(0)
        changed = True
    if changed: df.to_csv(path, index=False)

migrate_ap_schema(AP_CSV)

df_exp = load_data(USER_CSV, ['date', 'description', 'amount', 'category', 'source_file'])
df_inc = load_data(INCOME_CSV, ['date', 'source', 'amount', 'notes', 'source_file'])
df_ap = load_data(AP_CSV, ['invoice_date', 'vendor_name', 'invoice_number', 'amount', 'amount_paid', 'amount_remaining', 'due_date', 'status', 'source_file'])
df_hist = load_data(HISTORY_CSV, ['timestamp', 'filename', 'type', 'status'])

if not df_ap.empty:
    df_ap['amount_paid'] = pd.to_numeric(df_ap['amount_paid'], errors='coerce').fillna(0.0)
    df_ap['amount_remaining'] = (df_ap['amount'] - df_ap['amount_paid']).round(2)

def save_history(filename, doc_type, status):
    pd.DataFrame([[datetime.datetime.now(), filename, doc_type, status]], columns=['timestamp', 'filename', 'type', 'status']).to_csv(HISTORY_CSV, mode='a', header=not os.path.exists(HISTORY_CSV), index=False)

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown("<h2 class='gradient-text'>⚡ Clera.</h2>", unsafe_allow_html=True)
    if st.session_state.get('role') == 'admin':
        st.caption("🛡️ Signed in as Admin")
    menu_options = ["📊 Overview", "📥 Data Ingestion", "🤖 AP & AI Agent", "💵 Income Hub", "📝 Expense Ledger", "📈 ML Predictor"]
    if st.session_state.get('role') == 'admin':
        menu_options.append("🛡️ Admin Console")
    menu = st.radio("WORKSPACE", menu_options)
    st.divider()
    if st.button("Log out", use_container_width=True): st.session_state.update({'logged_in': False, 'username': '', 'role': ''}); st.rerun()

# --- MODULES ---
if menu == "📊 Overview":
    st.markdown(f"""
    <div class='hero-banner'>
        <div style='background: white; border-radius: 50%; padding: 5px; width: 70px; height: 70px; display: flex; align-items: center; justify-content: center;'>
            <img src='https://api.dicebear.com/7.x/notionists/svg?seed={active_user}&backgroundColor=ffffff' style='width: 60px; height: 60px; border-radius: 50%;'>
        </div>
        <div>
            <h1 style='margin: 0; font-weight: 800; font-size: 2rem; color: white;'>Welcome, {active_user.title()}</h1>
            <p style='margin: 0; opacity: 0.8; font-weight: 500;'>Here is your financial summary.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    total_in = df_inc['amount'].sum()
    total_out = df_exp['amount'].sum()
    net = total_in - total_out

    def fmt_currency(x):
        return f"-₹{abs(x):,.2f}" if x < 0 else f"₹{x:,.2f}"

    col1, col2, col3 = st.columns(3)
    col1.markdown(rich_card("Total Inflow", fmt_currency(total_in), "📈", "icon-green"), unsafe_allow_html=True)
    col2.markdown(rich_card("Total Outflow", fmt_currency(total_out), "📉", "icon-red"), unsafe_allow_html=True)
    col3.markdown(rich_card("Net Position", fmt_currency(net), "💰", "icon-blue" if net >= 0 else "icon-red"), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='section-title'>Spending Breakdown</div>", unsafe_allow_html=True)
        df_chart = df_exp[df_exp['amount'] > 0]
        if not df_chart.empty:
            st.plotly_chart(px.pie(df_chart, values='amount', names='category', hole=0.4), use_container_width=True)
        elif not df_exp.empty:
            st.warning("Your expense data has negative amounts. Purge the file and re-upload.")
        else:
            st.info("No expense data available to chart.")

elif menu == "📥 Data Ingestion":
    st.markdown("<h1 class='gradient-text'>Document Pipeline</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("<div class='section-title' style='border:none; margin-bottom:5px;'>Upload & Parse</div>", unsafe_allow_html=True)
        doc_type = st.radio("Select Document Type", ["Bank Statement (PDF)", "Vendor Invoice (PDF)"], horizontal=True)
        files = st.file_uploader("", type=["pdf"], accept_multiple_files=True)
        
        if files and st.button("Process via Gemini AI", type="primary", use_container_width=True):
            if DEFAULT_GEMINI_KEY == "YOUR_API_KEY_HERE":
                st.error("API Key missing. Add GEMINI_API_KEY to your Streamlit secrets.")
                st.stop()
            client = genai.Client(api_key=DEFAULT_GEMINI_KEY)
            
            for file in files:
                with st.spinner(f"Extracting data from {file.name}..."):
                    raw_text = "".join([page.extract_text() or "" for page in pdfplumber.open(file).pages])

                    with st.expander(f"🔍 Debug: extracted text from {file.name}"):
                        st.text(raw_text[:2000] if raw_text.strip() else "⚠️ No text extracted.")

                    if not raw_text.strip():
                        save_history(file.name, doc_type, "Failed - No text layer")
                        st.error(f"❌ {file.name}: No extractable text found.")
                        continue

                    try:
                        if doc_type == "Vendor Invoice (PDF)":
                            prompt = f"""Extract Accounts Payable Data. Return ONLY valid JSON, no markdown formatting.
                            Format: [{{"invoice_date": "YYYY-MM-DD", "vendor_name": "String", "invoice_number": "String", "amount": 0.0, "due_date": "YYYY-MM-DD"}}]
                            Text: {raw_text[:14000]}"""
                            expected_cols = ['invoice_date', 'vendor_name', 'invoice_number', 'amount', 'due_date']
                        else:
                            prompt = f"""Extract Bank Statement Data. Return ONLY valid JSON, no markdown formatting.
                            IMPORTANT sign convention: "amount" must be POSITIVE for money coming IN
                            and NEGATIVE for money going OUT.
                            Format: [{{"date": "YYYY-MM-DD", "description": "String", "amount": 0.0, "category": "String"}}]
                            Text: {raw_text[:14000]}"""
                            expected_cols = ['date', 'description', 'amount', 'category']
                        
                        response_obj = parse_document_with_retry(client.models, 'gemini-3.8-flash', contents=prompt)
                        res = response_obj.text.strip()
                        
                        res = res.replace("```json", "").replace("```", "").strip()
                        if "[" in res and "]" in res:
                            res = res[res.find("["):res.rfind("]")+1]
                        elif "{" in res and "}" in res:
                            res = res[res.find("{"):res.rfind("}")+1]

                        with st.expander(f"🤖 Debug: Gemini raw response for {file.name}"):
                            st.code(res if res else "(empty response)")

                        parsed_json = json.loads(res)
                        if isinstance(parsed_json, dict):
                            parsed_json = [parsed_json]
                            
                        parsed_data = pd.DataFrame(parsed_json)

                        for col in expected_cols:
                            if col not in parsed_data.columns:
                                parsed_data[col] = None
                        parsed_data = parsed_data[expected_cols]
                        parsed_data['amount'] = pd.to_numeric(parsed_data['amount'], errors='coerce').fillna(0)
                        
                        if doc_type == "Vendor Invoice (PDF)":
                            parsed_data['amount_paid'] = 0.0
                            parsed_data['amount_remaining'] = parsed_data['amount']
                            parsed_data = parsed_data.assign(status='Pending', source_file=file.name)
                            parsed_data = parsed_data[['invoice_date', 'vendor_name', 'invoice_number', 'amount', 'amount_paid', 'amount_remaining', 'due_date', 'status', 'source_file']]
                            parsed_data.to_csv(AP_CSV, mode='a', header=not os.path.exists(AP_CSV), index=False)
                            st.dataframe(parsed_data, use_container_width=True)
                        else:
                            parsed_data = parsed_data.assign(source_file=file.name)
                            income_rows = parsed_data[parsed_data['amount'] > 0].copy()
                            expense_rows = parsed_data[parsed_data['amount'] <= 0].copy()

                            if not income_rows.empty:
                                income_rows = income_rows.rename(columns={'description': 'source', 'category': 'notes'})
                                income_rows = income_rows[['date', 'source', 'amount', 'notes', 'source_file']]
                                income_rows.to_csv(INCOME_CSV, mode='a', header=not os.path.exists(INCOME_CSV), index=False)

                            if not expense_rows.empty:
                                expense_rows['amount'] = expense_rows['amount'].abs()
                                expense_rows = expense_rows[['date', 'description', 'amount', 'category', 'source_file']]
                                expense_rows.to_csv(USER_CSV, mode='a', header=not os.path.exists(USER_CSV), index=False)

                            st.write(f"💵 Logged as income: **{len(income_rows)}** transactions | 📉 Logged as expense: **{len(expense_rows)}** transactions")
                            st.dataframe(parsed_data, use_container_width=True)
                        
                        save_history(file.name, doc_type, "Success")
                        st.success(f"✅ Extracted {file.name} successfully!")
                    except Exception as e:
                        save_history(file.name, doc_type, "Failed")
                        st.error(f"Failed to parse {file.name}. Ensure it is a valid document. Error: {e}")
            load_data.clear()

    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container(border=True):
            st.markdown("<div class='section-title' style='margin-top:0;'>Upload History</div>", unsafe_allow_html=True)
            if not df_hist.empty:
                st.dataframe(df_hist.sort_values(by="timestamp", ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("No files processed yet.")
    with col2:
        with st.container(border=True):
            st.markdown("<div class='section-title' style='margin-top:0; color:#DC2626;'>🗑️ Delete Data</div>", unsafe_allow_html=True)
            if not df_hist.empty:
                file_to_del = st.selectbox("Select file to purge:", df_hist['filename'].unique())
                if st.button("Purge File & Records", type="primary"):
                    df_hist[df_hist['filename'] != file_to_del].to_csv(HISTORY_CSV, index=False)
                    if 'source_file' in df_ap.columns: df_ap[df_ap['source_file'] != file_to_del].to_csv(AP_CSV, index=False)
                    if 'source_file' in df_exp.columns: df_exp[df_exp['source_file'] != file_to_del].to_csv(USER_CSV, index=False)
                    st.success("File purged from workspace."); load_data.clear(); st.rerun()
            else:
                st.info("No data to delete.")

elif menu == "🤖 AP & AI Agent":
    st.markdown("<h1 class='gradient-text'>Accounts Payable Tracker</h1>", unsafe_allow_html=True)

    today = pd.Timestamp(datetime.date.today())
    if not df_ap.empty:
        pending_total = df_ap.loc[df_ap['status'] != 'Paid', 'amount_remaining'].sum()
        paid_total = df_ap['amount_paid'].sum()
        overdue_count = int(((df_ap['status'] != 'Paid') & (df_ap['due_date'] < today)).sum())
    else:
        pending_total, paid_total, overdue_count = 0, 0, 0

    m1, m2, m3 = st.columns(3)
    m1.markdown(rich_card("Pending Payables", f"₹{pending_total:,.2f}", "🧾", "icon-purple"), unsafe_allow_html=True)
    m2.markdown(rich_card("Paid Off", f"₹{paid_total:,.2f}", "✅", "icon-green"), unsafe_allow_html=True)
    m3.markdown(rich_card("Overdue Invoices", f"{overdue_count}", "⏰", "icon-red" if overdue_count else "icon-blue"), unsafe_allow_html=True)

    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        with st.container(border=True):
            st.markdown("<div class='section-title' style='margin-top:0;'>Vendor Ledger</div>", unsafe_allow_html=True)
            if not df_ap.empty:
                edited = st.data_editor(
                    df_ap,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "status": st.column_config.SelectboxColumn("Status", options=["Pending", "Paid", "Overdue"], required=True),
                        "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                        "amount_paid": st.column_config.NumberColumn("Amount Paid", format="₹%.2f", min_value=0.0, step=0.01),
                        "amount_remaining": st.column_config.NumberColumn("Amount Remaining", format="₹%.2f", disabled=True),
                        "invoice_date": st.column_config.DateColumn("Invoice Date"),
                        "due_date": st.column_config.DateColumn("Due Date"),
                    },
                )
                edited['amount_paid'] = pd.to_numeric(edited['amount_paid'], errors='coerce').fillna(0.0)
                edited['amount_remaining'] = (edited['amount'] - edited['amount_paid']).round(2)

                bcol1, bcol2 = st.columns(2)
                if bcol1.button("💾 Save AP Edits", type="primary", use_container_width=True):
                    edited.to_csv(AP_CSV, index=False)
                    st.success("Ledger updated!"); load_data.clear(); st.rerun()
                if bcol2.button("🧹 Remove Paid Invoices", use_container_width=True):
                    status_clean = edited['status'].astype(str).str.strip().str.casefold()
                    remaining = edited[status_clean != 'paid']
                    removed = len(edited) - len(remaining)
                    if removed == 0:
                        st.warning("No invoices are marked **Paid** yet.")
                    else:
                        remaining.to_csv(AP_CSV, index=False)
                        st.success(f"Removed {removed} paid invoice(s).")
                        load_data.clear(); st.rerun()
            else:
                st.info("Upload Vendor Invoices in the Data Ingestion tab.")
    with col2:
        with st.container(border=True):
            st.markdown("<div class='section-title' style='margin-top:0;'>💬 Ask Clera AP</div>", unsafe_allow_html=True)
            query = st.chat_input("E.g., 'Total unpaid invoices?'")
            if query:
                st.chat_message("user").write(query)
                if DEFAULT_GEMINI_KEY != "YOUR_API_KEY_HERE":
                    client = genai.Client(api_key=DEFAULT_GEMINI_KEY)
                    prompt = f"""You are Clera, a precise financial controller AI responsible for this company's Accounts Payable ledger.

DATA:
{df_ap.to_json(orient='records')}

USER QUESTION: {query}
"""
                    res_msg = parse_document_with_retry(client.models, 'gemini-3.8-flash', contents=prompt)
                    st.chat_message("assistant").write(res_msg.text)
                else:
                    st.chat_message("assistant").write("Please add GEMINI_API_KEY to your Streamlit secrets.")

elif menu == "📝 Expense Ledger":
    st.markdown("<h1 class='gradient-text'>Master Expense Ledger</h1>", unsafe_allow_html=True)

    st.markdown(rich_card("Total Logged Expenses", f"₹{df_exp['amount'].sum():,.2f}", "📉", "icon-red"), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**Manual Entry**")
        with st.form("add_exp", border=False):
            c1, c2, c3, c4 = st.columns(4)
            date = c1.date_input("Date")
            desc = c2.text_input("Description")
            amt = c3.number_input("Amount", min_value=0.0)
            cat = c4.text_input("Category")
            if st.form_submit_button("Add Record", type="primary") and desc:
                pd.DataFrame([[date, desc, amt, cat, 'Manual']], columns=df_exp.columns).to_csv(USER_CSV, mode='a', header=not os.path.exists(USER_CSV), index=False)
                load_data.clear(); st.rerun()
    
    with st.container(border=True):
        st.markdown("<div class='section-title' style='margin-top:0;'>Transaction Database</div>", unsafe_allow_html=True)
        edited = st.data_editor(df_exp, num_rows="dynamic", use_container_width=True, hide_index=True)
        if st.button("Save Database Changes", type="primary"): 
            edited.to_csv(USER_CSV, index=False); load_data.clear(); st.rerun()

elif menu == "💵 Income Hub":
    st.markdown("<h1 class='gradient-text'>Revenue Streams</h1>", unsafe_allow_html=True)

    st.markdown(rich_card("Total Logged Income", f"₹{df_inc['amount'].sum():,.2f}", "📈", "icon-green"), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**Log New Income**")
        with st.form("add_inc", border=False):
            c1, c2, c3 = st.columns(3)
            date = c1.date_input("Date")
            src = c2.text_input("Source")
            amt = c3.number_input("Amount", min_value=0.0)
            if st.form_submit_button("Log Income", type="primary") and src:
                pd.DataFrame([[date, src, amt, '', 'Manual']], columns=df_inc.columns).to_csv(INCOME_CSV, mode='a', header=not os.path.exists(INCOME_CSV), index=False)
                load_data.clear(); st.rerun()
            
    with st.container(border=True):
        st.markdown("<div class='section-title' style='margin-top:0;'>Income Records</div>", unsafe_allow_html=True)
        edited = st.data_editor(df_inc, num_rows="dynamic", use_container_width=True, hide_index=True)
        if st.button("Save Income Changes", type="primary"): 
            edited.to_csv(INCOME_CSV, index=False); load_data.clear(); st.rerun()

elif menu == "📈 ML Predictor":
    st.markdown("<h1 class='gradient-text'>AI Spending Forecast</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        if not df_exp.empty and len(df_exp) > 3:
            df_ml = df_exp.copy()
            df_ml['Days'] = (df_ml['date'] - df_ml['date'].min()).dt.days
            X = df_ml[['Days']]
            y = df_ml['amount']
            
            model = LinearRegression().fit(X, y)
            future_days = np.array([[X['Days'].max() + 30]])
            pred = model.predict(future_days)[0]
            
            st.markdown(rich_card("30-Day Outlay Projection", f"₹{pred:,.2f}", "🤖", "icon-blue"), unsafe_allow_html=True)
            st.plotly_chart(px.scatter(df_ml, x='date', y='amount', trendline="ols", title="Time-Series Expense Trajectory"), use_container_width=True)
        else:
            st.info("Log at least 4 transactions to generate ML projections.")

elif menu == "🛡️ Admin Console":
    st.markdown("<h1 class='gradient-text'>Admin Console</h1>", unsafe_allow_html=True)
    st.caption("Visible only to admin accounts. View and manage every workspace on this instance.")

    all_users = sorted(users_df['username'].unique())
    st.markdown(rich_card("Total Accounts", f"{len(all_users)}", "👥", "icon-blue"), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='section-title' style='margin-top:0;'>All Registered Accounts</div>", unsafe_allow_html=True)
        st.dataframe(users_df[['username', 'role']], use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.markdown("<div class='section-title' style='margin-top:0;'>Inspect a Workspace</div>", unsafe_allow_html=True)
        sel_user = st.selectbox("Select account", all_users)

        sel_exp = load_data(f"expenses_{sel_user}.csv", ['date', 'description', 'amount', 'category', 'source_file'])
        sel_inc = load_data(f"income_{sel_user}.csv", ['date', 'source', 'amount', 'notes', 'source_file'])
        sel_ap  = load_data(f"ap_{sel_user}.csv", ['invoice_date', 'vendor_name', 'invoice_number', 'amount', 'amount_paid', 'amount_remaining', 'due_date', 'status', 'source_file'])
        if not sel_ap.empty:
            sel_ap['amount_paid'] = pd.to_numeric(sel_ap['amount_paid'], errors='coerce').fillna(0.0)
            sel_ap['amount_remaining'] = (sel_ap['amount'] - sel_ap['amount_paid']).round(2)

        s_in, s_out = sel_inc['amount'].sum(), sel_exp['amount'].sum()
        m1, m2, m3 = st.columns(3)
        m1.markdown(rich_card("Inflow", f"₹{s_in:,.2f}", "📈", "icon-green"), unsafe_allow_html=True)
        m2.markdown(rich_card("Outflow", f"₹{s_out:,.2f}", "📉", "icon-red"), unsafe_allow_html=True)
        m3.markdown(rich_card("Net", f"₹{s_in - s_out:,.2f}", "💰", "icon-blue"), unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📝 Expenses", "💵 Income", "🧾 Accounts Payable"])
        with tab1: st.dataframe(sel_exp, use_container_width=True, hide_index=True)
        with tab2: st.dataframe(sel_inc, use_container_width=True, hide_index=True)
        with tab3: st.dataframe(sel_ap, use_container_width=True, hide_index=True)

    if sel_user != 'admin':
        with st.container(border=True):
            st.markdown("<div class='section-title' style='margin-top:0; color:#DC2626;'>⚠️ Danger Zone</div>", unsafe_allow_html=True)
            st.caption(f"Permanently delete the account **{sel_user}** and all of their data. This cannot be undone.")
            confirm = st.checkbox(f"I understand this will permanently delete {sel_user}'s account and all their data.")
            if st.button("Delete Account", type="primary", disabled=not confirm):
                users_df[users_df['username'] != sel_user].to_csv(USERS_FILE, index=False)
                for f in [f"expenses_{sel_user}.csv", f"income_{sel_user}.csv", f"ap_{sel_user}.csv", f"history_{sel_user}.csv"]:
                    if os.path.exists(f): os.remove(f)
                st.success(f"Deleted account '{sel_user}'."); load_data.clear(); st.rerun()