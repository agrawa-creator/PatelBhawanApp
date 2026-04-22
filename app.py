import streamlit as st
from supabase import create_client

# --- DIRECT CONFIGURATION (No Editing Needed) ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# UI Setup
st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")
st.title("🛒 Patel Bhavan Mart")
st.markdown("---")

try:
    # Fetching data from your 'inventory' table
    response = supabase.table("inventory").select("*").execute()
    items = response.data

    if not items:
        st.warning("Bhai, Table mein abhi koi item nahi hai. Supabase mein 'Insert' button dabakar data bharo!")
    else:
        # Creating a 3-column grid for the mart
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                # image url, Name, Price, MRP exact as per your screenshot
                img = item.get('image url', 'https://via.placeholder.com/150')
                name = item.get('Name', 'Unknown Item')
                mrp = item.get('MRP', 0)
                price = item.get('Price', 0)
                
                st.image(img, use_container_width=True)
                st.subheader(name)
                st.write(f"~~MRP: ₹{mrp}~~ | **Price: ₹{price}**")
                
                # Simple Order Section
                with st.expander(f"Order {name}"):
                    room = st.text_input("Room Number", key=f"room_{i}")
                    if st.button("Confirm Order", key=f"btn_{i}"):
                        if room:
                            st.balloons()
                            st.success(f"🚀 Order Done! Room {room} par 5 min mein pahunch jayega.")
                        else:
                            st.error("Bhai Room No. toh likh de!")

except Exception as e:
    st.error(f"Oye, abhi bhi error hai: {e}")
