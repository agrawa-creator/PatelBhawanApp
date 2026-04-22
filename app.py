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
if 'order_placed' not in st.session_state: st.session_state.order_placed = False

st.set_page_config(page_title="Patel Bhavan Mart | Elite", layout="wide", page_icon="💎")

# --- ULTRA MODERN CSS ---
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    
    /* Order Tracker Styling */
    .tracker-card { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); text-align: center; margin-bottom: 20px; }
    
    /* Product Card Styling */
    .product-card { border-radius: 20px; transition: 0.3s; padding: 15px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); }
    .product-card:hover { transform: translateY(-5px); border-color: #FFD700; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
    
    /* Custom Sidebar */
    .css-1d391kg { background-color: rgba(0, 0, 0, 0.5) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("<h1 style='text-align: center; color: #FFD700;'>💎 PATEL BHAVAN MART 💎</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Beyond Delivery. Room-to-Room Innovation.</p>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR: MANAGER GOD MODE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("Manager Portal")
    pwd = st.text_input("Access Key", type="password")
    
    if pwd == "Patel123":
        st.success("Authorized Access")
        # Today's Sales Counter
        st.metric("Today's Revenue", "₹1,240", delta="+12% from yesterday")
        
        # Fast Stock Control
        st.subheader("Inventory Quick-Fix")
        items_data = supabase.table("inventory").select("Name", "Stock").execute().data
        for item in items_data:
            if int(item['Stock']) < 5:
                st.warning(f"Refill {item['Name']}! (Only {item['Stock']} left)")
    else:
        st.info("Enter password for business analytics.")

# --- ORDER TRACKER (Unexpected 1st Year Feature) ---
if st.session_state.order_placed:
    with st.container():
        st.markdown("""
        <div class='tracker-card'>
            <h3 style='color: #FFD700;'>🚀 Order Status: On the Way!</h3>
            <p>Our delivery boy is currently near Wing-A.</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(65) # Show 65% complete
        if st.button("Close Tracker"):
            st.session_state.order_placed = False
            st.rerun()

# --- SEARCH & FILTER ---
col1, col2 = st.columns([2, 1])
with col1:
    search = st.text_input("🔍 What are you craving?", placeholder="Search chips, drinks, combos...")
with col2:
    cat = st.selectbox("Category", ["All", "Snacks", "Drinks", "Combos", "Essentials"])

# --- PRODUCT GRID ---
st.subheader("📦 Prime Selection")
try:
    query = supabase.table("inventory").select("*")
    if search: query = query.ilike("Name", f"%{search}%")
    if cat != "All": query = query.eq("Category", cat)
    items = query.execute().data
    
    cols = st.columns(3) # 3 Items per row for a more 'App' feel
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                st.image(item.get('image url'), use_container_width=True)
                st.subheader(item.get('Name'))
                
                price, stock = int(item.get('Price', 0)), int(item.get('Stock', 0))
                st.write(f"🏷️ Price: **₹{price}**")
                
                if stock > 0:
                    st.caption(f"Stock: {stock} units available")
                    if st.button(f"Add +", key=f"add_{item['id']}"):
                        st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': price, 's': stock}
                        st.toast(f"✅ {item['Name']} added to cart!")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.error("Out of Stock")
                st.markdown("</div>", unsafe_allow_html=True)
                st.write("") # Spacer

except Exception as e:
    st.error(f"Error: {e}")

# --- SHOPPING CART (SIDE DRAWER FEEL) ---
if st.session_state.cart:
    st.divider()
    st.header("🛒 Checkout")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        total = 0
        summary = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total += sub
            summary += f"• {name} (x{d['qty']})\n"
            st.write(f"**{name}** - ₹{sub}")
            if st.button(f"Remove", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()
                
    with c2:
        st.markdown(f"### Total: ₹{total}")
        n = st.text_input("Name")
        r = st.text_input("Room No.")
        
        if st.button("⚡ PLACE ORDER"):
            if n and r:
                # Update Stock
                for name, d in st.session_state.cart.items():
                    supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                
                notify(f"💎 *ELITE ORDER!*\nCustomer: {n}\nRoom: {r}\nItems:\n{summary}\nTotal: ₹{total}")
                st.session_state.cart = {}
                st.session_state.order_placed = True
                st.balloons()
                st.rerun()
            else:
                st.warning("Details missing!")

# --- FLOATING SUPPORT ---
st.markdown('<a href="https://wa.me/91XXXXXXXXXX" style="position:fixed; bottom:20px; left:20px; background:#25d366; color:white; padding:10px 20px; border-radius:30px; text-decoration:none; font-weight:bold; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">💬 Support</a>', unsafe_allow_html=True)
