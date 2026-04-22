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

st.set_page_config(page_title="Patel Bhavan Mart | Cyber", layout="wide", page_icon="⚡")

# --- ADVANCED CSS ---
st.markdown("""
    <style>
    /* Smooth Moving Tagline */
    .marquee-container {
        width: 100%; overflow: hidden; background: linear-gradient(90deg, #00FFC3, #0080FF);
        padding: 12px 0; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,255,195,0.3);
    }
    .marquee-text {
        display: inline-block; white-space: nowrap; font-weight: bold; color: black;
        font-size: 18px; animation: marquee 25s linear infinite;
    }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    /* Cyber Theme UI */
    .stApp { background: #050505; color: #00FFC3; }
    
    /* Fixed WhatsApp Floating Button */
    .whatsapp-btn { 
        position: fixed; bottom: 30px; right: 30px; background-color: #25d366; 
        color: white !important; padding: 15px 25px; border-radius: 50px; 
        font-weight: bold; box-shadow: 2px 5px 15px rgba(0,0,0,0.3); 
        z-index: 1000; text-decoration: none !important; display: flex; 
        align-items: center; gap: 10px; border: 2px solid white;
    }
    
    .cart-entry { background-color: rgba(255, 255, 255, 0.05); border-left: 5px solid #00FFC3; padding: 12px; border-radius: 12px; margin-bottom: 10px; }
    
    .stButton>button { border: 1px solid #00FFC3; background: transparent; color: #00FFC3; width: 100%; }
    .stButton>button:hover { background: #00FFC3; color: black !important; }
    
    /* Trending Item Design */
    .trending-box { background: rgba(0, 255, 195, 0.1); padding: 10px; border-radius: 8px; border: 1px solid #00FFC3; margin-bottom: 5px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOVING TAGLINE ---
st.markdown("""
    <div class="marquee-container">
        <div class="marquee-text">
            🚀 Bhai, ab room se baahar jaane ki zaroorat nahi... kyunki hum kar rahe hain ROOM-TO-ROOM Delivery! 🚀 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ⚡ Patel Bhavan Mart: Fastest in the Campus! ⚡ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 📦 Fresh Snacks & Drinks Delivered in 5-7 Mins! 📦
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager Console")
    pwd = st.text_input("Manager Password", type="password")
    
    if pwd == "Patel123":
        st.success("Manager Mode Active ✅")
        try:
            items_data = supabase.table("inventory").select("*").execute().data
            sel_name = st.selectbox("Select Product", [i['Name'] for i in items_data])
            curr = next(i for i in items_data if i['Name'] == sel_name)
            n_p = st.number_input("New Price", value=int(curr['Price']))
            n_s = st.number_input("New Stock", value=int(curr['Stock']))
            if st.button("Update Database"):
                supabase.table("inventory").update({"Price": n_p, "Stock": n_s}).eq("Name", sel_name).execute()
                st.rerun()
        except: st.error("DB Error")
    
    st.divider()
    
    # Leaderboard ki jagah "Live Trending"
    st.subheader("🔥 Trending Right Now")
    st.markdown("""
    <div class="trending-box">🍿 <b>Lays Magic Masala</b> - 14 orders</div>
    <div class="trending-box">🍫 <b>Oreo Chocolate</b> - 8 orders</div>
    <div class="trending-box">🥤 <b>Sting Energy</b> - 22 orders</div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("v2.0 - Developed for Patel Bhavan")

# --- WHATSAPP REDIRECT FIX (Yahan apna number daalo) ---
# Replace '919876543210' with your actual number
whatsapp_url = "https://wa.me/918864810011?text=Bhai%20ek%20help%20chahiye%20Patel%20Mart%20se"
st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN CONTENT ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
with col_h2:
    search = st.text_input("🔍 Search snacks...")

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
                    st.write(f"Price: ₹{p} | Stock: {s}")
                    if s > 0:
                        qty = st.number_input("Qty", 1, s, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': p, 's': s}
                            st.toast(f"✅ {item['Name']} added!")
                            time.sleep(0.5)
                            st.rerun()
                    else: st.error("Out of Stock")
    except Exception as e: st.error(f"Error: {e}")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart:
        st.info("Buffer Empty...")
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
        n = st.text_input("👤 Your Name")
        r = st.text_input("📍 Room No.")
        ph = st.text_input("📞 Phone No.")
        
        if st.button("🚀 EXECUTE ORDER"):
            if n and r and ph:
                try:
                    for name, d in st.session_state.cart.items():
                        new_s = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", d['id']).execute()
                    notify(f"🚀 *ORDER!*\nName: {n}\nRoom: {r}\nItems:\n{order_list}\nTotal: ₹{grand_total}")
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("ORDER EXECUTED!")
                    time.sleep(2)
                    st.rerun()
                except: st.error("Database Error!")
            else: st.warning("Details bharo!")
