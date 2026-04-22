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

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- CSS FOR DARK MODE COMPATIBILITY & CLEAN CART ---
st.markdown("""
    <style>
    /* Cart Item Styling - No more blank white boxes */
    .cart-entry {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .item-info {
        color: inherit;
    }
    .delivery-tag { 
        background: #FFD700; 
        color: #000; 
        padding: 2px 8px; 
        border-radius: 5px; 
        font-size: 11px; 
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SECURE MANAGER CONTROL ---
with st.sidebar:
    st.title("🛠️ Manager Panel")
    pwd = st.text_input("Manager Password", type="password")
    if pwd == "Patel123":
        st.session_state.shop_open = st.toggle("Open Shop", value=st.session_state.shop_open)
    st.divider()
    status_color = "green" if st.session_state.shop_open else "red"
    st.markdown(f"<h3 style='color:{status_color}; text-align:center;'>SHOP {'OPEN' if st.session_state.shop_open else 'CLOSED'}</h3>", unsafe_allow_html=True)

# --- HEADER ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
with col_h2:
    search = st.text_input("🔍 Search snacks...")

# --- CATEGORY ---
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Browse Categories", options=cats, default="All")

if not st.session_state.shop_open:
    st.warning("### 😴 Shop abhi band hai! Kal milte hain.")
    st.stop()

# --- MAIN LAYOUT ---
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
                    st.markdown("<span class='delivery-tag'>⏱️ 5 MINS</span>", unsafe_allow_html=True)
                    if stock > 0:
                        qty = st.number_input("Qty", 1, stock, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': price, 's': stock}
                            st.toast(f"✅ {item['Name']} added!")
                            time.sleep(0.5)
                            st.rerun()
                    else: st.error("Out of Stock")
    except Exception as e: st.error(f"Error: {e}")

with col_checkout:
    st.subheader("🧺 Checkout Basket")
    if not st.session_state.cart:
        st.info("Basket khali hai!")
    else:
        grand_total = 0
        order_list = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            grand_total += sub
            order_list += f"• {name} (x{d['qty']})\n"
            
            # --- IMPROVED CART ITEM UI ---
            st.markdown(f"""
                <div class="cart-entry">
                    <div class="item-info">
                        <b>{name}</b><br>
                        <small>{d['qty']} x ₹{d['price']} = ₹{sub}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🗑️ Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### Total: ₹{grand_total}")
        c_name = st.text_input("👤 Name")
        c_room = st.text_input("📍 Room")
        c_phone = st.text_input("📞 Phone")
        rating = st.select_slider("Rate Service", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 PLACE ORDER"):
            if c_name and c_room and c_phone:
                try:
                    for name, d in st.session_state.cart.items():
                        supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                    msg = f"🚀 *ORDER BY {c_name}*\nRoom: {c_room}\nPhone: {c_phone}\nRating: {rating}\nItems:\n{order_list}\nTotal: ₹{grand_total}"
                    notify(msg)
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Order Placed!")
                    time.sleep(2)
                    st.rerun()
                except: st.error("Stock update error!")
            else: st.warning("Details bharo!"
