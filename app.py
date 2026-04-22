import streamlit as st
from supabase import create_client
import requests

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM SETTINGS ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID = "7261699388"

def send_telegram_msg(msg):
    f_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    requests.get(f_url)

# --- SESSION STATE FOR CART ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# UI Setup
st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# Aesthetic CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .save-badge { background-color: #e6fffa; color: #00875a; padding: 5px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .cart-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #00CC66; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR CART SYSTEM ---
with st.sidebar:
    st.title("🛒 Your Cart")
    if not st.session_state.cart:
        st.write("Cart khali hai bhai! Kuch le lo.")
    else:
        total_bill = 0
        cart_summary = ""
        for item_name, details in list(st.session_state.cart.items()):
            subtotal = details['price'] * details['qty']
            total_bill += subtotal
            st.markdown(f"**{item_name}** (x{details['qty']}) - ₹{subtotal}")
            cart_summary += f"• {item_name} (x{details['qty']}) - ₹{subtotal}\n"
            if st.button(f"Remove {item_name}", key=f"remove_{item_name}"):
                del st.session_state.cart[item_name]
                st.rerun()
        
        st.markdown("---")
        st.subheader(f"Total: ₹{total_bill}")
        
        # Checkout Form in Sidebar
        room = st.text_input("Room No", placeholder="e.g. 101")
        phone = st.text_input("Phone", placeholder="Mobile number")
        
        if st.button("🚀 PLACE ORDER"):
            if room and phone and st.session_state.cart:
                final_msg = f"🔥 *NAYA CART ORDER!*\n\n📍 *Room:* {room}\n📞 *Phone:* {phone}\n\n*Items:*\n{cart_summary}\n💰 *FINAL BILL: ₹{total_bill}*"
                send_telegram_msg(final_msg)
                st.session_state.cart = {} # Clear cart
                st.balloons()
                st.success("Order ho gaya! Telegram par check kar.")
                st.rerun()
            else:
                st.error("Details bharo!")

# --- MAIN PAGE ---
st.title("🛒 Patel Bhavan Mart")
st.markdown("---")

try:
    response = supabase.table("inventory").select("*").execute()
    items = response.data

    if not items:
        st.warning("Inventory khali hai!")
    else:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                # Data
                img = item.get('image url', 'https://via.placeholder.com/150')
                name = item.get('Name', 'Item')
                mrp = int(item.get('MRP', 0))
                price = int(item.get('Price', 0))
                
                # Display
                st.image(img, use_container_width=True)
                st.subheader(name)
                st.write(f"~~MRP: ₹{mrp}~~ | **Price: ₹{price}**")
                
                # Savings
                if mrp > price:
                    st.markdown(f"<span class='save-badge'>You Save ₹{mrp-price}!</span>", unsafe_allow_html=True)
                
                # Add to Cart Logic
                qty = st.number_input("Qty", min_value=1, max_value=10, key=f"q_{i}")
                if st.button(f"➕ Add to Cart", key=f"add_{i}"):
                    st.session_state.cart[name] = {'price': price, 'qty': qty}
                    st.toast(f"{name} cart mein add ho gaya!")
                    st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
