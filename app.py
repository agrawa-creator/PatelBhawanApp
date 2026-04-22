import streamlit as st
from supabase import create_client
import requests
import time

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM SETTINGS ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID = "7261699388"

def send_telegram_msg(msg):
    f_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    try: requests.get(f_url)
    except: pass

# --- SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'order_success' not in st.session_state:
    st.session_state.order_success = False

# UI Setup
st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- CSS FOR HEADER & CART ---
st.markdown("""
    <style>
    .cart-counter {
        background-color: #FF4B4B;
        color: white;
        padding: 5px 12px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 20px;
        float: right;
    }
    .save-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER WITH CART COUNT ---
total_items_in_cart = sum(item['qty'] for item in st.session_state.cart.values())

col_t1, col_t2 = st.columns([4, 1])
with col_t1:
    st.title("🛍️ Patel Bhavan Mart")
with col_t2:
    # Ye upar arrow ke paas cart aur quantity dikhayega
    st.markdown(f"<div class='cart-counter'>🛒 {total_items_in_cart}</div>", unsafe_allow_html=True)

st.caption("Fresh items, Delivered in minutes to your room.")

# --- SUCCESS POPUP ---
if st.session_state.order_success:
    st.balloons()
    st.snow()
    st.success("### 🎉 ORDER PLACED SUCCESSFULLY!")
    time.sleep(3)
    st.session_state.order_success = False
    st.rerun()

# --- SIDEBAR (CHECKOUT) ---
with st.sidebar:
    st.markdown("## 🛒 My Basket")
    st.divider()
    if not st.session_state.cart:
        st.info("Basket khali hai bhai! 😋")
    else:
        total_bill = 0
        summary = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total_bill += sub
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{name}**\n{d['qty']} x ₹{d['price']} = ₹{sub}")
            if c2.button("🗑️", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
            summary += f"• {name} (x{d['qty']}) - ₹{sub}\n"
        
        st.divider()
        st.markdown(f"### Total: ₹{total_bill}")
        r = st.text_input("📍 Room No.", key="room_input")
        p = st.text_input("📞 Mobile No.", key="phone_input")
        
        if st.button("🚀 PLACE ORDER NOW"):
            if r and p:
                msg = f"📦 *NEW ORDER!*\n\n📍 *Room:* {r}\n📞 *Phone:* {p}\n\n*Items:*\n{summary}\n💰 *Total:* ₹{total_bill}"
                send_telegram_msg(msg)
                st.session_state.cart = {}
                st.session_state.order_success = True
                st.rerun()

# --- MAIN INVENTORY ---
try:
    res = supabase.table("inventory").select("*").execute()
    data = res.data

    if not data:
        st.info("Stock khatam hai!")
    else:
        cols = st.columns(3)
        for idx, item in enumerate(data):
            with cols[idx % 3]:
                st.image(item.get('image url'), use_container_width=True)
                st.subheader(item.get('Name'))
                
                m, p = int(item.get('MRP', 0)), int(item.get('Price', 0))
                if m > p:
                    st.markdown(f"<span class='save-badge'>YOU SAVE ₹{m-p}</span>", unsafe_allow_html=True)
                    st.write(f"~~₹{m}~~ **₹{p}**")
                else:
                    st.write(f"**₹{p}**")
                
                q = st.number_input("Qty", 1, 20, 1, key=f"q_{idx}")
                
                if st.button(f"➕ Add to Basket", key=f"btn_{idx}"):
                    # Update cart session
                    st.session_state.cart[item.get('Name')] = {'price': p, 'qty': q}
                    # Instant notification
                    st.toast(f"✅ {q} {item.get('Name')} added to basket!", icon="🛒")
                    time.sleep(0.1)
                    st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
