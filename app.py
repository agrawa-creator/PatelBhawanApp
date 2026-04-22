import streamlit as st
from supabase import create_client
import requests
import time
from datetime import datetime

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "7609324930"

def notify(msg):
    try:
        for cid in [CHAT_ID_1, CHAT_ID_2]:
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
    except:
        pass

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}

st.set_page_config(page_title="Patel Mart | Elite", layout="wide", page_icon="⚡")

# --- CUSTOM NEON CSS ---
st.markdown("""
    <style>
    .marquee-container {
        width: 100%; overflow: hidden; background: linear-gradient(90deg, #00FFC3, #0080FF);
        padding: 12px 0; border-radius: 12px; margin-bottom: 25px; display: flex;
    }
    .marquee-content { display: flex; white-space: nowrap; animation: marquee 15s linear infinite; }
    .marquee-text { font-weight: bold; color: black; font-size: 18px; padding-right: 60px; }
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
    .stButton>button { border: 1px solid #00FFC3; background: transparent; color: #00FFC3; width: 100%; border-radius: 10px; }
    .stButton>button:hover { background: #00FFC3; color: black !important; box-shadow: 0 0 15px #00FFC3; }
    </style>
    """, unsafe_allow_html=True)

# --- DYNAMIC TAGLINE ---
st.markdown("""
    <div class="marquee-container">
        <div class="marquee-content">
            <div class="marquee-text">🚀 Bhai, ab room se baahar jaane ki zaroorat nahi... ROOM-TO-ROOM Delivery is Live! 🚀 &nbsp;&nbsp;&nbsp; ⚡ Patel Mart: Fastest in Campus ⚡ &nbsp;&nbsp;&nbsp; 📦 No Delivery Charges! 📦 &nbsp;&nbsp;&nbsp;</div>
            <div class="marquee-text">🚀 Bhai, ab room se baahar jaane ki zaroorat nahi... ROOM-TO-ROOM Delivery is Live! 🚀 &nbsp;&nbsp;&nbsp; ⚡ Patel Mart: Fastest in Campus ⚡ &nbsp;&nbsp;&nbsp; 📦 No Delivery Charges! 📦 &nbsp;&nbsp;&nbsp;</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager Console")
    pwd = st.text_input("Password", type="password")
    if pwd == "Patel123":
        st.success("Authorized ✅")
        try:
            items_data = supabase.table("inventory").select("*").execute().data
            sel = st.selectbox("Quick Update Stock", [i['Name'] for i in items_data])
            curr = next(i for i in items_data if i['Name'] == sel)
            ns = st.number_input("Set Stock", value=int(curr['Stock']))
            if st.button("Save to DB"):
                supabase.table("inventory").update({"Stock": ns}).eq("Name", sel).execute()
                st.rerun()
        except: st.error("Manager DB Connection Lost")
    st.divider()
    st.caption("Patel Bhavan Mart v4.0")

# --- WHATSAPP SUPPORT (Number: 8864810011) ---
st.markdown('<a href="https://wa.me/918864810011?text=Bhai%20help%20chahiye" target="_blank" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN CONTENT ---
col_inv, col_checkout = st.columns([2, 1])

with col_inv:
    st.title("🛍️ Inventory")
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
                        if s <= 3: st.markdown(f"<p class='urgency-blink'>🔥 ONLY {s} LEFT!</p>", unsafe_allow_html=True)
                        else: st.caption(f"In Stock: {s}")
                        
                        if st.button(f"Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': p, 's': s}
                            st.toast(f"✅ {item['Name']} added!")
                            time.sleep(0.4)
                            st.rerun()
                    else: st.error("Out of Stock")
    except Exception as e: st.error(f"Inventory Error: {e}")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart:
        st.info("Basket khali hai...")
    else:
        total = 0
        order_sum = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total += sub
            order_sum += f"• {name} (x{d['qty']})\n"
            st.markdown(f"<div class='cart-entry'><b>{name}</b><br>1 x ₹{d['price']} = ₹{sub}</div>", unsafe_allow_html=True)
            if st.button(f"Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### TOTAL: ₹{total}")
        n = st.text_input("👤 Name")
        r = st.text_input("📍 Room No.")
        ph = st.text_input("📞 Mobile No.")
        rt = st.select_slider("Rating", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 EXECUTE ORDER"):
            if n and r and ph:
                try:
                    for name, d in st.session_state.cart.items():
                        new_s = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", d['id']).execute()
                    
                    notify(f"🚀 *ORDER ALERT!*\n\n👤 *Name:* {n}\n📍 *Room:* {r}\n📞 *Phone:* {ph}\n🌟 *Rating:* {rt}\n\n📦 *Items:*\n{order_sum}\n💰 *Total:* ₹{total}")
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("SUCCESS! watch the door in 5 mins.")
                    time.sleep(3)
                    st.rerun()
                except Exception as e: st.error(f"Checkout Error: {e}")
            else: st.warning("Pehle saari details bharo bhai!")
