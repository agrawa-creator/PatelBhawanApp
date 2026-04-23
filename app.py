import streamlit as st
from supabase import create_client
import requests
import time

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM BOT DETAILS ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "7609324930"

def notify_with_buttons(msg, phone, room, total):
    reply_markup = {
        "inline_keyboard": [
            [{"text": "📞 Call Customer", "url": f"tel:{phone}"}],
            [
                {"text": "💰 Paid", "url": f"https://wa.me/918864810011?text=Room%20{room}%20Paid"},
                {"text": "🚚 Delivered", "url": f"https://wa.me/918864810011?text=Room%20{room}%20Delivered"}
            ]
        ]
    }
    for cid in [CHAT_ID_1, CHAT_ID_2]:
        try:
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": cid, "text": msg, "parse_mode": "Markdown", "reply_markup": reply_markup})
        except: pass

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")

# --- CLEAN MATURE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .promo-box {
        background-color: #1E2633; border-left: 5px solid #3A8DFF; 
        padding: 12px; border-radius: 8px; margin-bottom: 15px; text-align: center;
    }
    .marquee-container {
        width: 100%; overflow: hidden; background: #262730;
        padding: 10px 0; border-radius: 8px; margin-bottom: 20px;
        border-bottom: 2px solid #4682B4; display: flex;
    }
    .marquee-content { display: flex; white-space: nowrap; animation: marquee 12s linear infinite; }
    .marquee-text { font-weight: bold; color: #4682B4; font-size: 16px; padding-right: 50px; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    .urgency-blink { color: #FF4B4B; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .whatsapp-btn { 
        position: fixed; bottom: 20px; right: 20px; background-color: #25D366; 
        color: white !important; padding: 10px 20px; border-radius: 30px; 
        font-weight: bold; z-index: 1000; text-decoration: none !important;
    }
    .stButton>button { border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- PROMO BOX ---
st.markdown("""
    <div class="promo-box">
        <span style="color: #3A8DFF; font-weight: bold;">📢 ANNOUNCEMENT:</span> 
        <span style="color: #E0E0E0;">Bhai, Exclusive Deals aur Stock Updates ke liye humara <b>WhatsApp Group</b> join karlo! 🔗</span>
        <br><a href="https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t" target="_blank" style="color: #25D366; text-decoration: none; font-weight: bold;">👉 Click to Join Group</a>
    </div>
""", unsafe_allow_html=True)

# --- TAGLINE ---
tag_txt = "🚀 ROOM-TO-ROOM DELIVERY ACTIVE! &nbsp;&nbsp; 📦 PATEL MART SPEED ⚡ &nbsp;&nbsp; 🍕 SNACKS & DRINKS &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f'<div class="marquee-container"><div class="marquee-content"><div class="marquee-text">{tag_txt * 4}</div><div class="marquee-text">{tag_txt * 4}</div></div></div>', unsafe_allow_html=True)

# --- SIDEBAR MANAGER ---
with st.sidebar:
    st.title("🛠️ Manager")
    pwd = st.text_input("Password", type="password")
    if pwd == "Patel123":
        st.success("Authorized")
        try:
            items_data = supabase.table("inventory").select("*").execute().data
            if items_data:
                sel = st.selectbox("Update Stock", [i['Name'] for i in items_data])
                ns = st.number_input("New Stock", value=0)
                if st.button("Save"):
                    supabase.table("inventory").update({"Stock": ns}).eq("Name", sel).execute()
                    st.rerun()
        except: st.error("Manager Access Error")
    
    st.divider()
    st.subheader("🔗 Community")
    st.markdown("[Join WhatsApp Group](https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t)")

st.markdown('<a href="https://wa.me/918864810011" target="_blank" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN ---
st.title("🛍️ Patel Bhavan Mart")
search = st.text_input("🔍 Search...")
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

col_inv, col_checkout = st.columns([2, 1])

with col_inv:
    try:
        # Better Fetching Logic
        res = supabase.table("inventory").select("*").execute()
