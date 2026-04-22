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

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    .cart-counter {
        background-color: #FF4B4B;
        color: white;
        padding: 6px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 18px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 10px;
        transition: 0.3s;
    }
    .save-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
    }
    .sidebar-content {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
cart_count = sum(item['qty'] for item in st.session_state.cart.values())
t1, t2 = st.columns([5, 1])
with t1:
    st.title("🛍️ Patel Bhavan Mart")
with t2:
    st.markdown(f"<div class='cart-counter'>🛒 Items: {cart_count}</div>", unsafe_allow_html=True)

st.caption("Hostel's Favorite Store | Fast Delivery 🚀")
st.divider()

# --- SUCCESS POPUP ---
if st.session_state.order_success:
    st.balloons()
    st.snow()
    st.success("### 🎉 ORDER BOOKED SUCCESSFULLY!")
    st.toast("Bhai order mil gaya, bas 5 min rukh!", icon="🔥")
    time.sleep(3)
    st.session_state.order_success = False
    st.rerun()

# --- SIDEBAR (ONLY PLACE TO BOOK/CHECKOUT) ---
with st.sidebar:
    st.markdown("## 🛒 My Shopping Basket")
    
    if not st.session_state.cart:
        st.info("Basket khali hai! Kuch add toh karo bhai. 😋")
    else:
        total_bill = 0
        order_summary_text = ""
        
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        for name, details in list(st.session_state.cart.items()):
            item_total = details['price'] * details['qty']
            total_bill += item_total
            
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{name}**\n{details['qty']} x ₹{details['price']} = **₹{item_total}**")
            if c2.button("🗑️", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
            
            order_summary_text += f"• {name} (x{details['qty']}) - ₹{item_total}\n"
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        st.markdown(f"### Total Bill: ₹{total_bill}")
        
        # Booking Details
        st.subheader("📝 Booking Details")
        room = st.text_input("Room Number", placeholder="Ex: 101")
        phone = st.text_input("Mobile Number", placeholder="Ex: 9876XXXXXX")
        
        if st.button("✅ CONFIRM & BOOK NOW"):
            if room and phone:
                final_msg = f"📦 *NAYA ORDER BOOKED!*\n\n" \
                            f"📍 *Room:* {room}\n" \
                            f"📞 *Phone:* {phone}\n\n" \
                            f"*Items List:*\n{order_summary_text}\n" \
                            f"💰 *Total Amount:* ₹{total_bill}\n\n" \
                            f"Jaldi pack kar lo bhai! 🔥"
                
                send_telegram_msg(final_msg)
                st.session_state.cart = {} # Cart clear after booking
                st.session_state.order_success = True
                st.rerun()
            else:
                st.error("Bhai Room aur Mobile no. toh daal do!")

# --- MAIN INVENTORY SHOWCASE ---
try:
    res = supabase.table("inventory").select("*").execute()
    data = res.data

    if not data:
        st.warning("Abhi shop par saaman khatam hai! 📦")
    else:
        # Display items in 3 columns
        cols = st.columns(3)
        for idx, item in enumerate(data):
            with cols[idx % 3]:
                # Item Details
                p_img = item.get('image url', 'https://via.placeholder.com/200')
                p_name = item.get('Name', 'Mart Item')
                p_mrp = int(item.get('MRP', 0))
                p_price = int(item.get('Price', 0))
                
                # Image & Styling
                st.image(p_img, use_container_width=True)
                st.subheader(p_name)
                
                # Savings calculation
                if p_mrp > p_price:
                    st.markdown(f"<span class='save-badge'>YOU SAVE ₹{p_mrp - p_price}</span>", unsafe_allow_html=True)
                    st.write(f"~~₹{p_mrp}~~ **₹{p_price}**")
                else:
                    st.write(f"**Price: ₹{p_price}**")
                
                # Qty Selection
                q = st.number_input("How many?", 1, 20, 1, key=f"q_main_{idx}")
                
                # ADD TO CART ONLY
                if st.button(f"➕ Add to Basket", key=f"add_main_{idx}"):
                    st.session_state.cart[p_name] = {'price': p_price, 'qty': q}
                    st.toast(f"✅ {q} {p_name} added! Check the basket on the left.", icon="🛒")
                    time.sleep(0.1)
                    st.rerun()

except Exception as e:
    st.error(f"Error fetching data: {e}")
