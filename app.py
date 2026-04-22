import streamlit as st
from supabase import create_client
import requests

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM SETTINGS (AB YE PAKKA CHALEGA) ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID = "7261699388"

def send_telegram_msg(msg):
    f_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    requests.get(f_url)

# UI Setup
st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")
st.title("🛒 Patel Bhavan Mart - Quick Delivery")
st.markdown("---")

try:
    response = supabase.table("inventory").select("*").execute()
    items = response.data

    if not items:
        st.warning("Bhai, Supabase mein items insert karo!")
    else:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                # image url, Name, Price, MRP columns matching your Supabase
                img = item.get('image url', 'https://via.placeholder.com/150')
                name = item.get('Name', 'Unknown Item')
                mrp = item.get('MRP', 0)
                price = item.get('Price', 0)
                
                st.image(img, use_container_width=True)
                st.subheader(name)
                st.write(f"~~MRP: ₹{mrp}~~ | **Price: ₹{price}**")
                
                with st.expander(f"Order {name}"):
                    room = st.text_input("Room Number", key=f"room_{i}")
                    phone = st.text_input("Mobile Number", key=f"phone_{i}")
                    
                    if st.button("Confirm Order", key=f"btn_{i}"):
                        if room and phone:
                            # Telegram Message Format
                            order_msg = f"🚀 *NAYA ORDER AAYA HAI!*\n\n" \
                                        f"📦 *Item:* {name}\n" \
                                        f"📍 *Room:* {room}\n" \
                                        f"📞 *Phone:* {phone}\n" \
                                        f"💰 *Bill:* ₹{price}\n\n" \
                                        f"Bhai jaldi nikal ja! 🏃‍♂️💨"
                            
                            send_telegram_msg(order_msg)
                            st.balloons()
                            st.success(f"Order Done! Room {room} par aa raha hoon.")
                        else:
                            st.error("Room aur Mobile dono bharo bhai!")

except Exception as e:
    st.error(f"Error: {e}")
