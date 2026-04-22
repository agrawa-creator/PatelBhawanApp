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

# --- CUSTOM AESTHETIC CSS ---
st.markdown("""
    <style>
    /* Cart Capsule Design */
    .cart-entry { 
        background-color: rgba(255, 255, 255, 0.07); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 12px; 
        border-left: 5px solid #00CC66;
    }
    .delivery-tag { 
        background: #FFD700; 
        color: #000; 
        padding: 3px 10px; 
        border-radius: 6px; 
        font-size: 11px; 
        font-weight: bold; 
    }
    .shop-status-ui { 
        font-size: 18px; 
        font-weight: bold; 
        padding: 12px; 
        border-radius: 12px; 
        text-align: center; 
        margin-bottom: 15px; 
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: MANAGER PANEL ---
with st.sidebar:
    st.title("🛠️ Manager Panel")
    pwd = st.text_input("Manager Password", type="password")
    if pwd == "Patel123":
        st.success("Welcome Manager! ✅")
        st.session_state.shop_open = st.toggle("Open Shop", value=st.session_state.shop_open)
    st.divider()
    if st.session_state.shop_open:
        st.markdown("<div style='background-color:#d4edda; color:#155724;' class='shop-status-ui'>🟢 SHOP OPEN</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color:#f8d7da; color:#721c24;' class='shop-status-ui'>🔴 SHOP CLOSED</div>", unsafe_allow_html=True)

# --- HEADER & SEARCH ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
    st.caption("Hostel's Favorite Mart | Fast Delivery ⚡")
with col_h2:
    search = st.text_input("🔍 Search snacks...", placeholder="Lays, Oreo...")

# --- CATEGORY FILTER ---
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

if not st.session_state.shop_open:
    st.warning("### 😴 Shop abhi band hai! Kal subah milte hain.")
    st.stop()

# --- MAIN LAYOUT ---
col_items, col_checkout = st.columns([2, 1])

with col_items:
    st.subheader("📦 Inventory")
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
                    mrp, price, stock = int(item.get('MRP', 0)), int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"~~₹{mrp}~~ | **₹{price}**")
                    st.markdown("<span class='delivery-tag'>⏱️ 5 MINS</span>", unsafe_allow_html=True)
                    
                    if stock > 0:
                        qty = st.number_input("Qty", 1, stock, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': price, 's': stock}
                            # --- POPUP FIX ---
                            st.toast(f"✅ {item['Name']} added!", icon="🛒")
                            time.sleep(1) # Popup dikhane ke liye wait
                            st.rerun()
                    else: st.error("Out of Stock ❌")
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
            
            # --- CLEAN ITEM UI ---
            st.markdown(f"""
            <div class='cart-entry'>
                <div><b>{name}</b><br><small>{d['qty']} x ₹{d['price']} = ₹{sub}</small></div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️ Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### Total Bill: ₹{grand_total}")
        st.info("💳 Pay via UPI/Cash on Delivery")
        
        # Customer Info
        c_name = st.text_input("👤 Your Name")
        c_room = st.text_input("📍 Room No.")
        c_phone = st.text_input("📞 Mobile No.")
        rating = st.select_slider("Rate Service", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 CONFIRM ORDER"):
            if c_name and c_room and c_phone:
                try:
                    # Update Stock
                    for name, d in st.session_state.cart.items():
                        new_stock = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_stock}).eq("id", d['id']).execute()
                    
                    # Notify Telegram
                    msg = f"🚀 *ORDER BY {c_name}*\n📍 Room: {c_room}\n📞 Phone: {c_phone}\n🌟 Rating: {rating}\nItems:\n{order_list}\nTotal: ₹{grand_total}"
                    notify(msg)
                    
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Done! Delivery for you is on the way.")
                    time.sleep(3)
                    st.rerun()
                except Exception as ex: 
                    st.error("Database update error! Check RLS.")
            else: 
                st.warning("Please enter all details!")
