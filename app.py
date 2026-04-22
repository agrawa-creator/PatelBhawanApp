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

st.set_page_config(page_title="Patel Bhavan Mart | Pro Max", layout="wide", page_icon="⚡")

# --- ADVANCED CSS (Animations & Floating Button) ---
st.markdown("""
    <style>
    /* Flash Deal Marquee */
    .marquee { background: linear-gradient(90deg, #FF4B4B, #FF914D); color: white; padding: 10px; font-weight: bold; border-radius: 10px; margin-bottom: 20px; text-align: center; }
    
    /* Floating WhatsApp Button */
    .whatsapp-btn { position: fixed; bottom: 20px; right: 20px; background-color: #25d366; color: white; padding: 15px; border-radius: 50px; text-align: center; font-size: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2); z-index: 999; text-decoration: none; }
    
    /* Cart & Items Styling */
    .cart-entry { background-color: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.1); padding: 12px; border-radius: 12px; margin-bottom: 10px; border-left: 5px solid #00CC66; }
    .low-stock-alert { color: #FF4B4B; font-weight: bold; font-size: 12px; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- FLASH DEAL MARQUEE ---
st.markdown('<div class="marquee">⚡ FLASH DEAL: Aaj Midnight Study Combo par ₹10 OFF! Room 210 se order karein! ⚡</div>', unsafe_allow_html=True)

# --- SIDEBAR: NEXT LEVEL MANAGER & STATS ---
with st.sidebar:
    st.title("🛠️ Manager Console")
    pwd = st.text_input("Admin Password", type="password")
    
    if pwd == "Patel123":
        st.success("Welcome, Boss! 😎")
        
        # Smart Inventory Alerts
        st.subheader("⚠️ Low Stock Alerts")
        items_data = supabase.table("inventory").select("*").execute().data
        low_stock_items = [i for i in items_data if int(i['Stock']) <= 3]
        if low_stock_items:
            for lsi in low_stock_items:
                st.error(f"Khatam hone wala hai: {lsi['Name']} (Bachay: {lsi['Stock']})")
        else:
            st.write("Sabar ka phal meetha hai, sab full hai! ✅")
        
        st.divider()
        
        # Stock & Price Editor
        st.subheader("✏️ Quick Update")
        item_names = [i['Name'] for i in items_data]
        sel_name = st.selectbox("Product", item_names)
        curr = next(i for i in items_data if i['Name'] == sel_name)
        
        c1, c2 = st.columns(2)
        with c1: n_p = st.number_input("Price", value=int(curr['Price']))
        with c2: n_s = st.number_input("Stock", value=int(curr['Stock']))
        
        if st.button("Save Changes"):
            supabase.table("inventory").update({"Price": n_p, "Stock": n_s}).eq("Name", sel_name).execute()
            st.toast("Updated!")
            time.sleep(1)
            st.rerun()

    st.divider()
    # Leaderboard (Point 5)
    st.subheader("🏆 Leaderboard")
    st.markdown("1. **Rahul (Room 102)** - 15 Orders\n2. **Sumit (Room 304)** - 12 Orders\n3. **Vivek (Room 211)** - 10 Orders")
    
    st.divider()
    # WhatsApp Support (Point 3)
    st.markdown('<a href="https://wa.me/91XXXXXXXXXX" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN PAGE ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
    st.write("Professional Hostel Startup | Faster than your WiFi ⚡")
with col_h2:
    search = st.text_input("🔍 Search snacks...")

# Category with "Combos" (Point 2)
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
                        st.markdown(f"📦 Stock: {s}")
                        if s <= 3: st.markdown("<p class='low-stock-alert'>⚠️ Low Stock!</p>", unsafe_allow_html=True)
                        
                        qty = st.number_input("Qty", 1, s, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': p, 's': s}
                            st.toast(f"✅ {item['Name']} added!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.error("Khatam Ho Gaya ❌")
    except Exception as e: st.error(f"Error: {e}")

with col_cart:
    st.subheader("🧺 Checkout")
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
        ph = st.text_input("📞 Mobile No.")
        rating = st.select_slider("Rate Experience", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 CONFIRM ORDER"):
            if n and r and ph:
                try:
                    for name, d in st.session_state.cart.items():
                        new_s = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", d['id']).execute()
                    
                    msg = f"🚀 *ORDER BY {n}*\nRoom: {r}\nPhone: {ph}\nRating: {rating}\nItems:\n{order_list}\nTotal: ₹{grand_total}"
                    notify(msg)
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Placed! 5 mins mein milte hain.")
                    time.sleep(2)
                    st.rerun()
                except: st.error("Stock update fail!")
            else: st.warning("Details bharo bhai!")
