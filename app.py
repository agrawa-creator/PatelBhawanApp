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

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
    <style>
    /* Main Background and Title */
    .main { background-color: #fcfcfc; }
    h1 { color: #1E1E1E; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Product Card Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: none;
        height: 3em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00CC66;
        color: white;
        transform: scale(1.02);
    }
    
    /* Savings Badge */
    .save-badge {
        background-color: #D4EDDA;
        color: #155724;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    /* Sidebar Styling */
    .css-1d391kg { background-color: #ffffff; border-left: 1px solid #eee; }
    .cart-header { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR CART SYSTEM ---
with st.sidebar:
    st.markdown("<div class='cart-header'>🛒 My Basket</div>", unsafe_allow_html=True)
    
    if not st.session_state.cart:
        st.info("Bhai, cart khali hai. Kuch tasty add karo! 😋")
    else:
        total_bill = 0
        cart_details_msg = ""
        
        for item_name, details in list(st.session_state.cart.items()):
            subtotal = details['price'] * details['qty']
            total_bill += subtotal
            
            # Individual Cart Item Row
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{item_name}**\n{details['qty']} x ₹{details['price']}")
            with col2:
                if st.button("❌", key=f"del_{item_name}"):
                    del st.session_state.cart[item_name]
                    st.rerun()
            
            cart_details_msg += f"• {item_name} (x{details['qty']}) - ₹{subtotal}\n"
            st.markdown("---")
        
        # Total and Checkout
        st.markdown(f"### Total Bill: `₹{total_bill}`")
        
        st.subheader("📍 Delivery Details")
        room_no = st.text_input("Room No.", placeholder="Ex: 102")
        phone_no = st.text_input("Mobile No.", placeholder="Ex: 9876XXXXXX")
        
        if st.button("🚀 Confirm Order"):
            if room_no and phone_no:
                order_summary = f"📦 *NEW ORDER - Patel Bhavan Mart*\n\n" \
                                f"👤 *Customer:* {phone_no}\n" \
                                f"🏢 *Room:* {room_no}\n\n" \
                                f"*Items:*\n{cart_details_msg}\n" \
                                f"💰 *Final Amount:* ₹{total_bill}\n\n" \
                                f"jaldi delivery de do! 🔥"
                
                send_telegram_msg(order_summary)
                st.session_state.cart = {} # Clear Cart
                st.balloons()
                st.success("Success! Order placed.")
                st.rerun()
            else:
                st.warning("Please fill Room and Phone details.")

# --- MAIN PAGE ---
st.markdown("# 🛍️ Patel Bhavan Mart")
st.caption("Fresh items, Delivered in minutes to your room.")
st.markdown("---")

try:
    # Fetch Data
    response = supabase.table("inventory").select("*").execute()
    inventory_data = response.data

    if not inventory_data:
        st.write("Abhi shop band hai, thodi der mein aao! 👋")
    else:
        # Display in 3 Columns
        main_cols = st.columns(3)
        for idx, item in enumerate(inventory_data):
            with main_cols[idx % 3]:
                # Extract Data
                p_img = item.get('image url', 'https://via.placeholder.com/200')
                p_name = item.get('Name', 'Mart Item')
                p_mrp = int(item.get('MRP', 0))
                p_price = int(item.get('Price', 0))
                
                # Card UI
                st.image(p_img, use_container_width=True)
                st.markdown(f"### {p_name}")
                
                # Price Section
                if p_mrp > p_price:
                    st.markdown(f"<div class='save-badge'>SAVE ₹{p_mrp - p_price}</div>", unsafe_allow_html=True)
                    st.write(f"~~₹{p_mrp}~~ **₹{p_price}**")
                else:
                    st.write(f"**Price: ₹{p_price}**")
                
                # Quantity and Add Button
                selected_qty = st.number_input("Quantity", min_value=1, max_value=20, value=1, key=f"q_input_{idx}")
                
                if st.button(f"🛒 Add to Basket", key=f"add_btn_{idx}"):
                    st.session_state.cart[p_name] = {'price': p_price, 'qty': selected_qty}
                    st.toast(f"✅ {p_name} added to basket!")
                    # Small pause to let toast show, then rerun to update sidebar
                    st.rerun()

except Exception as error:
    st.error(f"⚠️ Mart is facing an issue: {error}")
