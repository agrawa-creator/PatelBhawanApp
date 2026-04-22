import streamlit as st
from supabase import create_client
import requests

# 1. URL aur Key (Check karna quotes ke andar sahi hain na)
url = "https://tmwolhvzosjcegjmirrh.supabase.co/rest/v1/"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")
st.title("🛒 Patel Bhavan Mart - Quick Delivery")

# 2. Table Fetch (Yahan hum try-except laga rahe hain taaki error dikhe)
try:
    # AGAR TABLE KA NAAM CAPITAL 'I' HAI TOH YAHAN BHI 'Inventory' KAR DENA
    response = supabase.table("inventory").select("*").execute()
    items = response.data

    if not items:
        st.warning("Bhai, Supabase ki table mein koi item toh daal de! Table khali hai.")
    else:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                # Check karna ki column ke naam 'image_url', 'name', 'price' hi hain
                st.image(item.get('image_url', 'https://via.placeholder.com/150'), use_container_width=True)
                st.subheader(item.get('name', 'No Name'))
                st.write(f"**Price: ₹{item.get('price', 0)}**")
                
                with st.expander(f"Order {item.get('name')}"):
                    room = st.text_input("Room No", key=f"room_{i}")
                    if st.button("Confirm", key=f"btn_{i}"):
                        if room:
                            st.success(f"Order Done! Room {room}")
                            # Telegram wala part baad mein sahi karenge, pehle app load hone de
                        else:
                            st.error("Room No?")
except Exception as e:
    st.error(f"Supabase se connection nahi ho raha. Error: {e}")
