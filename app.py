import streamlit as st
from supabase import create_client
import requests
import time

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM BOT ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "6927591741"

def notify_with_buttons(msg, phone, room):
    reply_markup = {
        "inline_keyboard": [
            [{"text": "📞 Call Customer", "url": f"tel:{phone}"}],
            [{"text": "💰 Mark Paid", "url": f"https://wa.me/918864810011?text=Room%20{room}%20Paid"}]
        ]
    }
    for cid in [CHAT_ID_1, CHAT_ID_2]:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": cid, "text": msg, "parse_mode": "Markdown", "reply_markup": reply_markup})

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'order_placed' not in st.session_state: st.session_state.order_placed = False

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")

# --- CLEAN CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .marquee-container {
        width: 100%; overflow: hidden; background: #262730;
        padding: 10px 0; border-radius: 8px; margin-bottom: 20px;
        border-bottom: 2px solid #4682B4; display: flex;
    }
    .marquee-content { display: flex; white-space: nowrap; animation: marquee 10s linear infinite; }
    .marquee-text { font-weight: bold; color: #4682B4; font-size: 16px; padding-right: 50px; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    
    /* Order Status Box */
    .status-box {
        background-color: #1E2633; padding: 20px; border-radius: 12px;
        text-align: center; border: 1px solid #4682B4; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TAGLINE ---
tag_txt = "🚀 ROOM-TO-ROOM DELIVERY ACTIVE! &nbsp;&nbsp; 📦 PATEL MART SPEED ⚡ &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f'<div class="marquee-container"><div class="marquee-content"><div class="marquee-text">{tag_txt * 4}</div><div class="marquee-text">{tag_txt * 4}</div></div></div>', unsafe_allow_html=True)

# --- ORDER PLACED SCREEN ---
if st.session_state.order_placed:
    st.balloons()
    st.markdown("""
        <div class="status-box">
            <h2 style="color: #25D366;">🎉 Order Confirmed!</h2>
            <p>Bhai, tera order humare paas pohoch gaya hai.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Live Delivery Tracker Animation
    with st.status("Tracking your snacks...", expanded=True) as status:
        st.write("Order Received by Manager... ✅")
        time.sleep(2)
        st.write("Packing your items... 🎒")
        time.sleep(2)
        st.write("Delivery boy on the way to your Room... 🏃‍♂️")
        time.sleep(2)
        status.update(label="Order Dispatched!", state="complete", expanded=False)
    
    if st.button("Order More Items"):
        st.session_state.order_placed = False
        st.rerun()
    st.stop()

# --- MAIN SHOP ---
col_inv, col_checkout = st.columns([2, 1])

with col_inv:
    st.title("🛍️ Patel Bhavan Mart")
    try:
        data = supabase.table("inventory").select("*").execute().data
        grid = st.columns(2)
        for idx, item in enumerate(data or []):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    p, s = int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"Price: ₹{p}")
                    if s > 0:
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': p, 's': s}
                            st.toast(f"Added {item['Name']}")
                            time.sleep(0.3)
                            st.rerun()
                    else: st.error("Out of Stock")
    except: st.error("DB Load Error")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart: st.info("Basket khali hai")
    else:
        total = 0
        order_details = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total += sub
            order_details += f"{name}, "
            st.write(f"**{name}** - ₹{sub}")
            if st.button(f"Remove", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.write(f"### Total: ₹{total}")
        n, r, ph = st.text_input("Name"), st.text_input("Room"), st.text_input("Phone")
        
        if st.button("🚀 CONFIRM ORDER"):
            if n and r and ph:
                for name, d in st.session_state.cart.items():
                    supabase.table("inventory").update({"Stock": d['s'] - 1}).eq("id", d['id']).execute()
                
                msg = f"🚀 *NEW ORDER!*\n👤 Name: {n}\n📍 Room: {r}\n📞 Phone: {ph}\n📦 Items: {order_details}\n💰 Total: ₹{total}"
                notify_with_buttons(msg, ph, r)
                
                st.session_state.cart = {}
                st.session_state.order_placed = True
                st.rerun()
            else: st.warning("Details bharo!")
