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
    # Buttons ka logic
    buttons = {
        "inline_keyboard": [
            [
                {"text": "📞 Call Customer", "url": f"tel:{phone}"},
            ],
            [
                {"text": "💰 Mark as PAID", "url": f"https://wa.me/918864810011?text=Order%20at%20Room%20{room}%20of%20Rs.{total}%20is%20PAID"},
                {"text": "🚚 DELIVERED", "url": f"https://wa.me/918864810011?text=Order%20for%20Room%20{room}%20is%20DELIVERED"}
            ]
        ]
    }
    
    for cid in [CHAT_ID_1, CHAT_ID_2]:
        requests.post(
            f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
            json={
                "chat_id": cid, 
                "text": msg, 
                "parse_mode": "Markdown",
                "reply_markup": buttons
            }
        )

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- AESTHETIC CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0F1116; color: #E0E0E0; }
    .marquee-container {
        width: 100%; overflow: hidden; background: #1E2633;
        padding: 10px 0; border-radius: 8px; margin-bottom: 25px;
        border-bottom: 2px solid #3A8DFF; display: flex;
    }
    .marquee-content { display: flex; white-space: nowrap; animation: marquee 12s linear infinite; }
    .marquee-text { font-weight: bold; color: #3A8DFF; font-size: 18px; padding-right: 50px; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    .urgency-blink { color: #FF4B4B; font-weight: bold; animation: blinker 0.8s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .whatsapp-btn { position: fixed; bottom: 30px; right: 30px; background-color: #2DB842; color: white !important; padding: 12px 20px; border-radius: 10px; font-weight: bold; z-index: 1000; text-decoration: none !important; }
    .cart-entry { background-color: #1C2128; border-left: 4px solid #3A8DFF; padding: 10px; border-radius: 8px; margin-bottom: 8px; }
    .stButton>button { background-color: #1E2633; color: #3A8DFF; border: 1px solid #3A8DFF; border-radius: 8px; width: 100%; transition: 0.2s; }
    .stButton>button:hover { background-color: #3A8DFF; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MOVING LINE ---
moving_text = "🚀 ROOM-TO-ROOM DELIVERY ACTIVE! &nbsp;&nbsp; 📦 NO NEED TO LEAVE YOUR ROOM! &nbsp;&nbsp; ⚡ PATEL MART SPEED ⚡ &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f'<div class="marquee-container"><div class="marquee-content"><div class="marquee-text">{moving_text * 4}</div><div class="marquee-text">{moving_text * 4}</div></div></div>', unsafe_allow_html=True)

# --- SIDEBAR: SIMPLE MANAGER ---
with st.sidebar:
    st.title("🛠️ Manager")
    pwd = st.text_input("Password", type="password")
    if pwd == "Patel123":
        st.success("Authorized")
        items_data = supabase.table("inventory").select("*").execute().data
        sel = st.selectbox("Update Stock", [it['Name'] for it in items_data])
        curr = next(it for it in items_data if it['Name'] == sel)
        ns = st.number_input("Set Stock", value=int(curr['Stock']))
        if st.button("Update"):
            supabase.table("inventory").update({"Stock": ns}).eq("Name", sel).execute()
            st.rerun()

st.markdown('<a href="https://wa.me/918864810011" target="_blank" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN SHOP ---
st.title("🛍️ Patel Bhavan Mart")
search = st.text_input("🔍 Search...")
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

col_inv, col_checkout = st.columns([2, 1])

with col_inv:
    try:
        db_query = supabase.table("inventory").select("*")
        if search: db_query = db_query.ilike("Name", f"%{search}%")
        if selected_cat != "All": db_query = db_query.eq("Category", selected_cat)
        data = db_query.execute().data
        grid = st.columns(2)
        for idx, item in enumerate(data or []):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    p, s = int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"Price: ₹{p}")
                    if s > 0:
                        if s <= 3: st.markdown(f"<p class='urgency-blink'>🔥 ONLY {s} LEFT!</p>", unsafe_allow_html=True)
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': p, 's': s}
                            st.toast(f"✅ Added {item['Name']}")
                            time.sleep(0.3)
                            st.rerun()
                    else: st.error("Out of Stock")
    except: st.error("DB Error")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart: st.info("Empty")
    else:
        grand_total = 0
        order_list = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            grand_total += sub
            order_list += f"{name}, "
            st.markdown(f"<div class='cart-entry'><b>{name}</b> - ₹{sub}</div>", unsafe_allow_html=True)
            if st.button(f"Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.write(f"### Total: ₹{grand_total}")
        n, r, ph = st.text_input("Name"), st.text_input("Room No."), st.text_input("Mobile No.")
        
        if st.button("🚀 CONFIRM ORDER"):
            if n and r and ph:
                # Update Stock in DB
                for name, d in st.session_state.cart.items():
                    supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                
                # New Notification with Buttons
                msg = f"🚀 *NEW ORDER!*\n\n👤 *Name:* {n}\n📍 *Room:* {r}\n📞 *Phone:* {ph}\n\n📦 *Items:* {order_list}\n💰 *Total:* ₹{grand_total}\n\n⚠️ *STATUS: PENDING*"
                notify_with_buttons(msg, ph, r, grand_total)
                
                st.session_state.cart = {}
                st.balloons()
                st.success("Order Placed! Check Telegram.")
                time.sleep(2)
                st.rerun()
            else: st.warning("Fill details!")
