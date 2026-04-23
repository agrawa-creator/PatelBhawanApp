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
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": cid, "text": msg, "parse_mode": "Markdown", "reply_markup": reply_markup})

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")

# --- CSS ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager")
    pwd = st.text_input("Password", type="password")
    if pwd == "Patel123":
        st.success("Authorized")
        try:
            items_data = supabase.table("inventory").select("*").execute().data
            sel = st.selectbox("Update Stock", [i['Name'] for i in items_data])
            ns = st.number_input("New Stock", value=0)
            if st.button("Save"):
                supabase.table("inventory").update({"Stock": ns}).eq("Name", sel).execute()
                st.rerun()
        except: st.error("DB Load Error")
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
        data = supabase.table("inventory").select("*").execute().data
        if search: data = [i for i in data if search.lower() in i['Name'].lower()]
        if selected_cat != "All": data = [i for i in data if i.get('Category') == selected_cat]
        
        grid = st.columns(2)
        for idx, item in enumerate(data or []):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    p, s = int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"Price: ₹{p} | Stock: {s}")
                    if s > 0:
                        if s <= 3: st.markdown(f"<p class='urgency-blink'>🔥 ONLY {s} LEFT!</p>", unsafe_allow_html=True)
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': p, 's': s}
                            st.toast(f"✅ {item['Name']} added")
                            time.sleep(0.3)
                            st.rerun()
                    else: st.error("Out of Stock")
    except: st.error("Database Load Error")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart: st.info("Empty")
    else:
        grand_total = 0
        order_list = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            grand_total += sub
            order_list += f"{name} (x1), "
            st.write(f"**{name}** - ₹{sub}")
            if st.button(f"Remove", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.write(f"### Total: ₹{grand_total}")
        n, r, ph = st.text_input("Name"), st.text_input("Room No."), st.text_input("Phone")
        
        if st.button("🚀 CONFIRM ORDER"):
            if n and r and ph:
                try:
                    # Update DB (Fixed Logic)
                    for name, d in st.session_state.cart.items():
                        new_stock = max(0, d['s'] - 1)
                        supabase
