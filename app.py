import streamlit as st
from supabase import create_client
import requests
import time

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- TELEGRAM ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "7609324930"

def notify(msg):
    for cid in [CHAT_ID_1, CHAT_ID_2]:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}

st.set_page_config(page_title="Patel Bhavan Mart | Pro", layout="wide", page_icon="⚡")

# --- ADVANCED CSS ---
st.markdown("""
    <style>
    /* New Dynamic Tagline Marquee */
    .marquee { 
        background: linear-gradient(90deg, #1e3c72, #2a5298); 
        color: white; 
        padding: 12px; 
        font-weight: bold; 
        border-radius: 12px; 
        margin-bottom: 25px; 
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .whatsapp-btn { position: fixed; bottom: 30px; right: 30px; background-color: #25d366; color: white; padding: 15px 25px; border-radius: 50px; font-weight: bold; box-shadow: 2px 5px 15px rgba(0,0,0,0.3); z-index: 1000; text-decoration: none; display: flex; align-items: center; gap: 10px; }
    
    .trending-item { background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 8px; }
    
    .cart-entry { background-color: rgba(255, 255, 255, 0.08); border-left: 5px solid #00CC66; padding: 12px; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- NEW TAGLINE (Point 2) ---
st.markdown('<div class="marquee">🚀 Bhai, ab room se baahar jaane ki zaroorat nahi... kyunki hum kar rahe hain ROOM-TO-ROOM Delivery! 🚀</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager Console")
    pwd = st.text_input("Manager Password", type="password")
    
    if pwd == "Patel123":
        st.success("Manager Mode Active")
        # Quick Editor (Pehle jaisa)
        items_data = supabase.table("inventory").select("*").execute().data
        st.subheader("Edit Inventory")
        sel_name = st.selectbox("Product", [i['Name'] for i in items_data])
        curr = next(i for i in items_data if i['Name'] == sel_name)
        n_p = st.number_input("Price", value=int(curr['Price']))
        n_s = st.number_input("Stock", value=int(curr['Stock']))
        if st.button("Update"):
            supabase.table("inventory").update({"Price": n_p, "Stock": n_s}).eq("Name", sel_name).execute()
            st.rerun()
    
    st.divider()
    
    # --- TRENDING ITEMS (Leaderboard ki jagah - Point 1) ---
    st.subheader("🔥 Trending Today")
    st.markdown("""
    <div class='trending-item'>🍿 <b>Lays Magic Masala</b> - 14 sold</div>
    <div class='trending-item'>🍫 <b>Oreo Chocolate</b> - 9 sold</div>
    <div class='trending-item'>🥤 <b>Coke (Can)</b> - 7 sold</div>
    """, unsafe_allow_html=True)
    
    st.divider()
    # WhatsApp Button
    st.markdown('<a href="https://wa.me/91XXXXXXXXXX" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN CONTENT ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
with col_h2:
    search = st.text_input("🔍 Search snacks...")

cats = ["All", "Snacks", "Drinks", "Biscuits", "Combos", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

col_inv, col_cart = st.columns([2, 1])

with col_inv:
    try:
        db_query = supabase.table("inventory").select("*")
        if search: db_query = db_query.ilike("Name", f"%{search}%")
        if selected_cat != "All": db_query = db_query.eq("Category", selected_cat)
        
        data = db_query.execute().data
        grid = st.columns(2)
        for idx, item in enumerate(data or []):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    p, s = int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"**Price: ₹{p}**")
                    if s > 0:
                        st.caption(f"Stock: {s}")
                        qty = st.number_input("Qty", 1, s, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': p, 's': s}
                            st.toast(f"✅ {item['Name']} added!")
                            time.sleep(0.8)
                            st.rerun()
                    else: st.error("Out of Stock")
    except Exception as e: st.error(f"Error: {e}")

with col_cart:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart:
        st.info("Basket khali hai!")
    else:
        grand_total = 0
        order_list = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            grand_total += sub
            order_list += f"• {name} (x{d['qty']})\n"
            st.markdown(f"<div class='cart-entry'><b>{name}</b><br>{d['qty']} x ₹{d['price']} = ₹{sub}</div>", unsafe_allow_html=True)
            if st.button(f"🗑️ Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### Total: ₹{grand_total}")
        n = st.text_input("👤 Your Name")
        r = st.text_input("📍 Room No.")
        ph = st.text_input("📞 Phone No.")
        rating = st.select_slider("Rate Service", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 CONFIRM ORDER"):
            if n and r and ph:
                try:
                    for name, d in st.session_state.cart.items():
                        new_s = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", d['id']).execute()
                    
                    msg = f"🚀 *ORDER! (By {n})*\n📍 Room: {r}\n📞 Phone: {ph}\nRating: {rating}\nItems:\n{order_list}\nTotal: ₹{grand_total}"
                    notify(msg)
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Done! Delivery for you is coming.")
                    time.sleep(2)
                    st.rerun()
                except: st.error("Database Error!")
            else: st.warning("Details bharo!")
