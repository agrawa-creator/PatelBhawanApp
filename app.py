import streamlit as st
from supabase import create_client
import requests

# 1. Supabase aur Telegram ki details (Tujhe ye Supabase settings se milengi)
url = "https://tmwolhvzosjcegjmirrh.supabase.co/rest/v1/"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

TELEGRAM_TOKEN = "TERA_BOT_TOKEN"
CHAT_ID = "TERI_CHAT_ID"

def send_notif(msg):
    f_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    requests.get(f_url)

# 2. UI Design
st.set_page_config(page_title="Patel Bhavan Marg", layout="wide")
st.title("🛒 Patel Bhavan Marg - Quick Delivery")

# 3. Items Fetch Karna
items = supabase.table("inventory").select("*").eq("is_available", True).execute()

# 4. Items Display (Aesthetic Grid)
cols = st.columns(3)
for i, item in enumerate(items.data):
    with cols[i % 3]:
        st.image(item['image_url'], use_column_width=True)
        st.subheader(f"{item['name']}")
        st.write(f"~~MRP: ₹{item['mrp']}~~ | **Price: ₹{item['price']}**")
        
        # Order Form
        with st.expander(f"Order {item['name']}"):
            room = st.text_input("Room No.", key=f"room_{item['id']}")
            qty = st.number_input("Quantity", min_value=1, key=f"qty_{item['id']}")
            if st.button("Confirm Order", key=f"btn_{item['id']}"):
                if room:
                    msg = f"🚀 *NAYA ORDER!*\n\n📍 Room: {room}\n📦 Item: {item['name']}\n🔢 Qty: {qty}\n💰 Total: ₹{int(item['price'])*qty}"
                    send_notif(msg)
                    st.success("Bhai order aa gaya! 5 min mein milte hain.")
                else:
                    st.error("Room Number toh daal de bhai!")
