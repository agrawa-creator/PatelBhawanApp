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

# UI Setup
st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# Custom CSS for Aesthetic Look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #00CC66; color: white; }
    .stExpander { border: 1px solid #f0f2f6; border-radius: 10px; }
    .save-text { color: #00CC66; font-weight: bold; font-size: 14px; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🛒 Patel Bhavan Mart")
st.subheader("Fastest Delivery in the Hostel! 🔥")
st.markdown("---")

try:
    response = supabase.table("inventory").select("*").execute()
    items = response.data

    if not items:
        st.warning("Bhai, Table khali hai! Supabase mein data bharo.")
    else:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                # Data Extraction
                img = item.get('image url', 'https://via.placeholder.com/150')
                name = item.get('Name', 'Unknown Item')
                mrp = int(item.get('MRP', 0))
                price = int(item.get('Price', 0))
                savings = mrp - price
                
                # Aesthetic Display
                st.image(img, use_container_width=True)
                st.subheader(name)
                st.write(f"~~MRP: ₹{mrp}~~ | **Price: ₹{price}**")
                
                if savings > 0:
                    st.markdown(f"<p class='save-text'>✅ You save ₹{savings} on this item!</p>", unsafe_allow_html=True)
                
                # Order Section with Quantity
                with st.expander(f"Order {name}"):
                    qty = st.number_input("How many?", min_value=1, max_value=10, value=1, key=f"qty_{i}")
                    total_bill = price * qty
                    st.write(f"**Total Bill: ₹{total_bill}**")
                    
                    room = st.text_input("Room Number", key=f"room_{i}", placeholder="e.g. 101")
                    phone = st.text_input("Mobile Number", key=f"phone_{i}", placeholder="e.g. 9876543210")
                    
                    if st.button(f"Confirm {qty} {name}", key=f"btn_{i}"):
                        if room and phone:
                            # Telegram Message
                            order_msg = f"🚀 *NAYA ORDER!*\n\n" \
                                        f"📦 *Item:* {name}\n" \
                                        f"🔢 *Quantity:* {qty}\n" \
                                        f"📍 *Room:* {room}\n" \
                                        f"📞 *Phone:* {phone}\n" \
                                        f"💰 *Total Bill:* ₹{total_bill}\n\n" \
                                        f"Bhai jaldi nikal ja! 🏃‍♂️💨"
                            
                            send_telegram_msg(order_msg)
                            st.balloons()
                            st.success(f"Order Done! Total: ₹{total_bill}. Milte hain room {room} par!")
                        else:
                            st.error("Bhai details toh bharo!")

except Exception as e:
    st.error(f"Error: {e}")
