import streamlit as st
from supabase import create_client

# URL aur Key tumhari wali hi rehne dena
url = "https://tmwolhvzosjcegjmirrh.supabase.co/rest/v1/"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")
st.title("🛒 Patel Bhavan Mart - Quick Delivery")

try:
    # Tumhari table ka naam 'inventory' small mein hi hai
    response = supabase.table("inventory").select("*").execute()
    items = response.data

    if not items:
        st.warning("Bhai, Table khali hai!")
    else:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                # Yahan humne Name, Price aur image url ko wahi rakha hai jo screenshot mein hai
                st.image(item.get('image url', 'https://via.placeholder.com/150'), use_container_width=True)
                st.subheader(item.get('Name', 'Item'))
                st.write(f"MRP: ₹{item.get('MRP', 0)} | **Price: ₹{item.get('Price', 0)}**")
                
                with st.expander(f"Order {item.get('Name')}"):
                    room = st.text_input("Room No", key=f"room_{i}")
                    if st.button("Confirm Order", key=f"btn_{i}"):
                        if room:
                            st.success(f"Bhai Room {room} ke liye order ho gaya!")
                        else:
                            st.error("Room No?")
except Exception as e:
    st.error(f"Error: {e}")
