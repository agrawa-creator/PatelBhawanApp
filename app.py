import streamlit as st
from supabase import create_client
import requests

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# Yahan apni details dalo (Maine bataya tha @BotFather aur @IDBot se milegi)
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID = "7261699388"

def send_telegram_msg(msg):
    if TELE_TOKEN != "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs":
        f_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
        requests.get(f_url)

# UI
st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")
st.title("🛒 Patel Bhavan Mart")

try:
    response = supabase.table("inventory").select("*").execute()
    items = response.data

    if not items:
        st.warning("Supabase mein items add karo bhai!")
    else:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                st.image(item.get('image url', 'https://via.placeholder.com/150'), use_container_width=True)
                st.subheader(item.get('Name'))
                st.write(f"**Price: ₹{item.get('Price')}**")
                
                with st.expander(f"Order {item.get('Name')}"):
                    room = st.text_input("Room Number", key=f"room_{i}")
                    phone = st.text_input("Mobile Number", key=f"phone_{i}")
                    if st.button("Confirm Order", key=f"btn_{i}"):
                        if room and phone:
                            # Ye message tere Telegram par aayega
                            msg = f"🔥 *NAYA ORDER!*\n\n📦 Item: {item.get('Name')}\n📍 Room: {room}\n📞 Phone: {phone}\n💰 Price: ₹{item.get('Price')}"
                            send_telegram_msg(msg)
                            
                            st.balloons()
                            st.success(f"Order Done! Bhai {room} par aa raha hoon.")
                        else:
                            st.error("Room aur Mobile dono daalna zaroori hai!")
except Exception as e:
    st.error(f"Error: {e}")
