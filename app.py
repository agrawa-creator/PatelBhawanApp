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
if 'shop_open' not in st.session_state: st.session_state.shop_open = True

st.set_page_config(page_title="Patel Bhavan Mart | Pro", layout="wide", page_icon="🛒")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; transition: 0.3s; }
    .cart-item { background: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #00CC66; }
    .delivery-tag { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .shop-status-ui { font-size: 18px; font-weight: bold; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SECURE MANAGER CONTROL ---
with st.sidebar:
    st.title("🛠️ Control Panel")
    pwd = st.text_input("Manager Password", type="password")
    
    if pwd == "Patel123":
        st.success("Welcome, Manager!")
        st.session_state.shop_open = st.toggle("Shop Open", value=st.session_state.shop_open)
    
    st.divider()
    if st.session_state.shop_open:
        st.markdown("<div style='background-color:#d4edda; color:#155724;' class='shop-status-ui'>🟢 SHOP OPEN</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color:#f8d7da; color:#721c24;' class='shop-status-ui'>🔴 SHOP CLOSED</div>", unsafe_allow_html=True)

# --- HEADER & SEARCH ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
    st.write("Professional Campus Store ⚡")
with col_h2:
    search = st.text_input("🔍 Search snacks...")

# --- CATEGORY FILTER ---
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

if not st.session_state.shop_open:
    st.warning("### 😴 Shop abhi band hai! Kal milte hain.")
    st.stop()

# --- MAIN CONTENT ---
col_items, col_checkout = st.columns([2, 1])

with col_items:
    try:
        db_query = supabase.table("inventory").select("*")
        if search: db_query = db_query.ilike("Name", f"%{search}%")
        if selected_cat != "All": db_query = db_query.eq("Category", selected_cat)
        
        items = db_query.execute().data
        grid = st.columns(2)
        for idx, item in enumerate(items):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    mrp, price, stock = int(item.get('MRP', 0)), int(item.get('Price', 0)), int(item.get('Stock', 0))
                    
                    st.write(f"~~₹{mrp}~~ | **₹{price}**")
                    st.markdown("<span class='delivery-tag'>⏱️ 5-7 MINS</span>", unsafe_allow_html=True)
                    
                    if stock > 0:
                        qty = st.number_input("Qty", 1, stock, 1, key=f"qty_{item['id']}")
                        if st.button(f"Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': price, 's': stock}
                            st.toast(f"✅ Added {item['Name']}!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.error("Out of Stock")
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
            st.markdown(f"<div class='cart-item'><b>{name}</b><br>{d['qty']} x ₹{d['price']} = ₹{sub}</div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### Total: ₹{grand_total}")
        
        # PAYMENT SECTION (Point 5)
        st.warning("💳 **Payment:** Pay via UPI on Delivery")
        
        c_name = st.text_input("👤 Name")
        c_room = st.text_input("📍 Room No.")
        c_phone = st.text_input("📞 Mobile No.")
        
        if st.button("🚀 CONFIRM ORDER"):
            if c_name and c_room and c_phone:
                try:
                    for name, d in st.session_state.cart.items():
                        supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                    
                    msg = f"🚀 *ORDER BY {c_name}*\n📍 Room: {c_room}\n📞 Phone: {c_phone}\nItems:\n{order_list}\n💰 Total: ₹{grand_total}"
                    notify(msg)
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Order Placed!")
                    time.sleep(3)
                    st.rerun()
                except: st.error("Stock error!")
            else: st.warning("Details bharo!")
