import streamlit as st
from supabase import create_client
import requests
import time
import random

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM BOT ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "7609324930"

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
if 'orders_done' not in st.session_state: st.session_state.orders_done = random.randint(34, 47)

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")

# --- CLEAN AESTHETIC CSS ---
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

    .lucky-box {
        background: rgba(70, 130, 180, 0.1);
        border: 1px dashed #4682B4; padding: 10px; border-radius: 10px;
        text-align: center; margin-bottom: 20px;
    }
    
    .wa-receipt-btn {
        display: inline-block; width: 100%; padding: 12px;
        background-color: #25D366; color: white !important;
        text-align: center; border-radius: 8px; font-weight: bold;
        text-decoration: none; margin-top: 10px;
    }
    
    .stButton>button { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- LUCKY CHALLENGE ---
remaining = 50 - st.session_state.orders_done
st.markdown(f"""
    <div class="lucky-box">
        <span style="color:#4682B4; font-weight:bold;">🎁 LUCKY ORDER CHALLENGE:</span> 
        Next <b>{remaining} orders</b> mein se ek winner ko milegi <b>Free Chocolate!</b> 🍫
    </div>
""", unsafe_allow_html=True)

# --- TAGLINE ---
tag_txt = "🚀 ROOM-TO-ROOM DELIVERY ACTIVE! &nbsp;&nbsp; 📦 PATEL MART SPEED ⚡ &nbsp;&nbsp;&nbsp;&nbsp;"
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
            if st.button("Update"):
                supabase.table("inventory").update({"Stock": ns}).eq("Name", sel).execute()
                st.rerun()
        except: st.error("DB Error")

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
                # Update DB
                for name, d in st.session_state.cart.items():
                    supabase.table("inventory").update({"Stock": d['s'] - 1}).eq("id", d['id']).execute()
                
                # Notify Telegram
                msg = f"🚀 *NEW ORDER!*\n👤 Name: {n}\n📍 Room: {r}\n📞 Phone: {ph}\n📦 Items: {order_details}\n💰 Total: ₹{total}"
                notify_with_buttons(msg, ph, r)
                
                # Digital Receipt Logic
                wa_msg = f"Bhai {n}, tera order Patel Mart par confirm ho gaya! Bill: ₹{total}. Room {r} pe 5 min mein pohoch rahe hain! ⚡"
                wa_url = f"https://wa.me/91{ph}?text={wa_msg.replace(' ', '%20')}"
                
                st.session_state.cart = {}
                st.session_state.orders_done += 1
                st.balloons()
                st.success("Order Placed!")
                st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-receipt-btn">📲 Get Digital Receipt</a>', unsafe_allow_html=True)
                time.sleep(5)
                st.rerun()
            else: st.warning("Details bharo!")
