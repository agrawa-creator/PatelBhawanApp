import streamlit as st
from supabase import create_client
import requests
import time

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "7609324930"

def notify(msg):
    for cid in [CHAT_ID_1, CHAT_ID_2]:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}

st.set_page_config(page_title="Patel Bhavan Mart | Elite", layout="wide", page_icon="⚡")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .marquee-container {
        width: 100%; overflow: hidden; background: linear-gradient(90deg, #00FFC3, #0080FF);
        padding: 12px 0; border-radius: 12px; margin-bottom: 25px; display: flex;
    }
    .marquee-content { display: flex; white-space: nowrap; animation: marquee 15s linear infinite; }
    .marquee-text { font-weight: bold; color: black; font-size: 18px; padding-right: 50px; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

    .stApp { background: #050505; color: #00FFC3; }
    
    .urgency-blink {
        color: #FF3131; font-weight: bold; font-size: 13px;
        text-shadow: 0 0 5px #FF3131; animation: blinker 0.8s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0; } }

    .whatsapp-btn { 
        position: fixed; bottom: 30px; right: 30px; background-color: #25d366; 
        color: white !important; padding: 15px 25px; border-radius: 50px; 
        font-weight: bold; box-shadow: 2px 5px 15px rgba(0,0,0,0.3); z-index: 1000;
        text-decoration: none !important; border: 2px solid white;
    }
    
    .cart-entry { background-color: rgba(255, 255, 255, 0.05); border-left: 5px solid #00FFC3; padding: 12px; border-radius: 12px; margin-bottom: 10px; }
    .stButton>button { border: 1px solid #00FFC3; background: transparent; color: #00FFC3; width: 100%; }
    .stButton>button:hover { background: #00FFC3; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- TAGLINE ---
st.markdown("""
    <div class="marquee-container">
        <div class="marquee-content">
            <div class="marquee-text">🚀 Bhai, ROOM-TO-ROOM Delivery is Live! 🚀 &nbsp;&nbsp;&nbsp; ⚡ Patel Mart: Fastest in Campus ⚡ &nbsp;&nbsp;&nbsp; 📦 Fresh Snacks Delivered in 5 Mins! 📦 &nbsp;&nbsp;&nbsp;</div>
            <div class="marquee-text">🚀 Bhai, ROOM-TO-ROOM Delivery is Live! 🚀 &nbsp;&nbsp;&nbsp; ⚡ Patel Mart: Fastest in Campus ⚡ &nbsp;&nbsp;&nbsp; 📦 Fresh Snacks Delivered in 5 Mins! 📦 &nbsp;&nbsp;&nbsp;</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager")
    pwd = st.text_input("Password", type="password")
    if pwd == "Patel123":
        st.success("Manager Mode Active ✅")
        # DB update logic stays here...
    st.divider()
    st.info("Patel Bhavan Mart v3.0")

# --- WHATSAPP ---
st.markdown('<a href="https://wa.me/918864810011" target="_blank" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN CONTENT ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1: st.title("🛍️ Patel Bhavan Mart")
with col_h2: search = st.text_input("🔍 Search...")

cats = ["All", "Snacks", "Drinks", "Biscuits", "Combos", "Others"]
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
                        qty = st.number_input("Qty", 1, s, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': p, 's': s}
                            st.rerun()
                    else: st.error("Out of Stock")
    except: st.error("DB Error")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart:
        st.info("Basket is empty...")
    else:
        grand_total = 0
        order_list = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            grand_total += sub
            order_list += f"• {name} (x{d['qty']})\n"
            st.markdown(f"<div class='cart-entry'><b>{name}</b><br>{d['qty']} x ₹{d['price']} = ₹{sub}</div>", unsafe_allow_html=True)
            if st.button(f"Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### TOTAL: ₹{grand_total}")
        n = st.text_input("👤 Name")
        r = st.text_input("📍 Room No.")
        ph = st.text_input("📞 Mobile No.")
        
        if st.button("🚀 EXECUTE ORDER"):
            if n and r and ph:
                try:
                    for name, d in st.session_state.cart.items():
                        new_s = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", d['id']).execute()
                    
                    # --- FIXED TELEGRAM MSG (Added Mobile No.) ---
                    notify(f"🚀 *NEW ORDER!*\n\n👤 *Name:* {n}\n📍 *Room:* {r}\n📞 *Phone:* {ph}\n\n📦 *Items:*\n{order_list}\n💰 *Total:* ₹{grand_total}")
                    
                    st.session_state.cart = {}
                    st.balloons()
                    
                    # --- RATING SYSTEM ---
                    st.success("Order Placed Successfully!")
                    st.write("### Rate your experience:")
                    st.feedback("stars") # This adds the 5-star rating widget
                    
                    time.sleep(3)
                    st.rerun()
                except: st.error("Error!")
            else: st.warning("Please fill all details!")
