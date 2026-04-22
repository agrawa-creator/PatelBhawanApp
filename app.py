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

# --- CUSTOM CSS FOR NO-SIDEBAR LOOK ---
st.markdown("""
    <style>
    .cart-section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid #00CC66;
    }
    .product-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stButton>button { border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🛍️ Patel Bhavan Mart")
st.caption("No Sidebar, No Jhanjhat! Direct Order Karo 🔥")
st.divider()

# --- SUCCESS POPUP ---
if st.session_state.order_success:
    st.balloons()
    st.success("### 🎉 ORDER BOOKED! Check your Telegram.")
    time.sleep(3)
    st.session_state.order_success = False
    st.rerun()

# --- MAIN LAYOUT (Inventory | Cart) ---
col_inventory, col_cart = st.columns([2, 1])

with col_inventory:
    st.subheader("📦 Select Items")
    try:
        res = supabase.table("inventory").select("*").execute()
        data = res.data
        if not data:
            st.info("Stock khatam hai!")
        else:
            # Grid of 2 columns for items
            i_cols = st.columns(2)
            for idx, item in enumerate(data):
                with i_cols[idx % 2]:
                    st.image(item.get('image url'), use_container_width=True)
                    st.markdown(f"**{item.get('Name')}**")
                    p = int(item.get('Price', 0))
                    st.write(f"Price: ₹{p}")
                    
                    q = st.number_input("Qty", 1, 10, 1, key=f"q_{idx}")
                    if st.button(f"➕ Add", key=f"add_{idx}"):
                        st.session_state.cart[item.get('Name')] = {'price': p, 'qty': q}
                        st.toast(f"✅ {item.get('Name')} added!")
                        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

with col_cart:
    st.markdown("<div class='cart-section'>", unsafe_allow_html=True)
    st.subheader("🛒 Your Basket")
    
    if not st.session_state.cart:
        st.write("Basket khali hai. Kuch add karo!")
    else:
        total = 0
        summary = ""
        for name, details in list(st.session_state.cart.items()):
            sub = details['price'] * details['qty']
            total += sub
            st.write(f"**{name}** (x{details['qty']}) - ₹{sub}")
            summary += f"• {name} (x{details['qty']}) - ₹{sub}\n"
            if st.button("Delete", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.markdown(f"### Total: ₹{total}")
        
        # Immediate Booking Form
        r = st.text_input("Room No.")
        p = st.text_input("Phone No.")
        
        if st.button("✅ CONFIRM ORDER"):
            if r and p:
                msg = f"🚀 *DIRECT ORDER!*\n\n📍 *Room:* {r}\n📞 *Phone:* {p}\n\n*Items:*\n{summary}\n💰 *Total:* ₹{total}"
                send_telegram_msg(msg)
                st.session_state.cart = {}
                st.session_state.order_success = True
                st.rerun()
            else:
                st.error("Details bharo!")
    st.markdown("</div>", unsafe_allow_html=True)
