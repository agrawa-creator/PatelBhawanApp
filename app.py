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

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- CSS ---
st.markdown("""
    <style>
    .cart-entry { background-color: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.1); padding: 12px; border-radius: 12px; margin-bottom: 10px; border-left: 5px solid #00CC66; }
    .stock-badge { background: #e1f5fe; color: #01579b; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 14px; }
    .delivery-tag { background: #FFD700; color: #000; padding: 2px 8px; border-radius: 5px; font-size: 11px; font-weight: bold; }
    .manager-card { background: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ADVANCED MANAGER CONSOLE ---
with st.sidebar:
    st.title("🛠️ Manager Console")
    pwd = st.text_input("Manager Password", type="password")
    
    if pwd == "Patel123":
        st.success("Admin Mode: ON ✅")
        
        # 1. Earnings & Stats (Dummy logic - based on current inventory for demo)
        st.subheader("📊 Business Stats")
        items_data = supabase.table("inventory").select("*").execute().data
        total_items = len(items_data)
        st.metric("Total Products", total_items)
        
        st.divider()
        
        # 2. Inventory & Price Editor
        st.subheader("✏️ Edit Items")
        item_names = [i['Name'] for i in items_data]
        sel_name = st.selectbox("Select Product", item_names)
        
        # Current data for selected item
        curr_item = next(item for item in items_data if item['Name'] == sel_name)
        
        col1, col2 = st.columns(2)
        with col1:
            new_p = st.number_input("New Price", value=int(curr_item['Price']))
        with col2:
            new_s = st.number_input("New Stock", value=int(curr_item['Stock']))
            
        if st.button("Update Product"):
            supabase.table("inventory").update({"Price": new_p, "Stock": new_s}).eq("Name", sel_name).execute()
            st.toast(f"✅ Updated {sel_name}!")
            time.sleep(1)
            st.rerun()
            
        st.divider()
        st.info("Tip: Order records Telegram par check karein.")
    else:
        st.info("Admin password dalo stats aur stock manage karne ke liye.")

# --- HEADER & SEARCH ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
    st.caption("24/7 Hostel Snacks Delivery ⚡")
with col_h2:
    search = st.text_input("🔍 Search items...")

# --- CATEGORY ---
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

# --- MAIN LAYOUT ---
col_items, col_checkout = st.columns([2, 1])

with col_items:
    try:
        db_query = supabase.table("inventory").select("*")
        if search: db_query = db_query.ilike("Name", f"%{search}%")
        if selected_cat != "All": db_query = db_query.eq("Category", selected_cat)
        
        items = db_query.execute().data
        grid = st.columns(2)
        for idx, item in enumerate(items or []):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    p, s = int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"**Price: ₹{p}**")
                    
                    if s > 0:
                        st.markdown(f"📦 <span class='stock-badge'>In Stock: {s}</span>", unsafe_allow_html=True)
                        qty = st.number_input("Qty", 1, s, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': p, 's': s}
                            st.toast(f"✅ {item['Name']} added!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("Khatam Ho Gaya ❌")
                    
                    st.markdown("<span class='delivery-tag'>⏱️ 5-7 MINS</span>", unsafe_allow_html=True)
    except Exception as e: st.error(f"Error: {e}")

with col_checkout:
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
            if st.button(f"🗑️ Remove", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### Total: ₹{grand_total}")
        c_name = st.text_input("👤 Your Name")
        c_room = st.text_input("📍 Room No.")
        c_phone = st.text_input("📞 Mobile No.")
        rating = st.select_slider("Rate us", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 CONFIRM ORDER"):
            if c_name and c_room and c_phone:
                try:
                    for name, d in st.session_state.cart.items():
                        new_stock = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_stock}).eq("id", d['id']).execute()
                    
                    msg = f"🚀 *ORDER! (By {c_name})*\n📍 Room: {c_room}\n📞 Phone: {c_phone}\n🌟 Rating: {rating}\nItems:\n{order_list}\nTotal: ₹{grand_total}"
                    notify(msg)
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Order Placed! 5 mins mein milte hain.")
                    time.sleep(2)
                    st.rerun()
                except: st.error("Database Error!")
            else: st.warning("Pehle details bharo!")
