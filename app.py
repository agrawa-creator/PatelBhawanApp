import streamlit as st
from supabase import create_client
import requests
import time
import qrcode
from io import BytesIO

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
if 'pay_step' not in st.session_state: st.session_state.pay_step = False

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- CSS FOR UI ---
st.markdown("""
    <style>
    .cart-entry { background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 12px; border-radius: 12px; margin-bottom: 8px; }
    .timer-box { font-size: 24px; font-weight: bold; color: #FF4B4B; text-align: center; border: 2px solid #FF4B4B; border-radius: 10px; padding: 10px; }
    .delivery-tag { background: #FFD700; color: #000; padding: 2px 8px; border-radius: 5px; font-size: 11px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: MANAGER PANEL ---
with st.sidebar:
    st.title("🛠️ Manager Panel")
    pwd = st.text_input("Admin Password", type="password")
    if pwd == "Patel123":
        st.session_state.shop_open = st.toggle("Shop Open", value=st.session_state.shop_open)
    st.divider()
    st.markdown(f"### STATUS: {'🟢 OPEN' if st.session_state.shop_open else '🔴 CLOSED'}")

# --- SHOP CHECK ---
if not st.session_state.shop_open:
    st.warning("### 😴 Mart is currently closed. See you later!")
    st.stop()

# --- HEADER ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1: st.title("🛍️ Patel Bhavan Mart")
with col_h2: search = st.text_input("🔍 Search snacks...")

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
        for idx, item in enumerate(items):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    mrp, price, stock = int(item.get('MRP', 0)), int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"~~₹{mrp}~~ | **₹{price}**")
                    st.markdown("<span class='delivery-tag'>⏱️ 5 MINS DELIVERY</span>", unsafe_allow_html=True)
                    if stock > 0:
                        qty = st.number_input("Qty", 1, stock, 1, key=f"q_{item['id']}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': price, 's': stock}
                            st.toast(f"✅ {item['Name']} added!")
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
            st.markdown(f"<div class='cart-entry'><b>{name}</b> (x{d['qty']}) - ₹{sub}</div>", unsafe_allow_html=True)
            if st.button(f"Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### Total Amount: ₹{grand_total}")
        
        c_name = st.text_input("👤 Full Name", key="user_name")
        c_room = st.text_input("📍 Room No.", key="user_room")
        c_phone = st.text_input("📞 Mobile No.", key="user_phone")
        rating = st.select_slider("Rate us", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")

        if not st.session_state.pay_step:
            if st.button("🚀 PROCEED TO PAYMENT"):
                if c_name and c_room and c_phone:
                    st.session_state.pay_step = True
                    st.rerun()
                else: st.warning("Pehle details bharo bhai!")
        
        else:
            # --- DYNAMIC PAYMENT SYSTEM ---
            st.markdown("### 💳 Scan & Pay")
            # Yahan apni UPI ID dalo
            upi_id = "agarwalchirag4391@okicici" 
            upi_url = f"upi://pay?pa={upi_id}&pn=PatelMart&am={grand_total}&cu=INR&tn=OrderBy_{c_name}"
            
            qr = qrcode.make(upi_url)
            buf = BytesIO()
            qr.save(buf)
            st.image(buf, caption="Scan this QR with PhonePe/GPay/Paytm", width=250)
            
            # TIMER UI
            st.markdown("<div class='timer-box'>QR Expires in: <span id='timer'>05:00</span></div>", unsafe_allow_html=True)
            st.warning("⚠️ Payment karke hi 'Confirm' dabayein. Screenshot zaroori hai!")
            
            if st.button("✅ PAYMENT DONE - CONFIRM ORDER"):
                try:
                    for name, d in st.session_state.cart.items():
                        supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                    
                    msg = f"💰 *PAID ORDER! (By {c_name})*\n📍 Room: {c_room}\n📞 Phone: {c_phone}\n🌟 Rating: {rating}\nItems:\n{order_list}\nTotal: ₹{grand_total}"
                    notify(msg)
                    
                    st.session_state.cart = {}
                    st.session_state.pay_step = False
                    st.balloons()
                    st.success("Order Placed! Delivery in 5 mins.")
                    time.sleep(3)
                    st.rerun()
                except: st.error("Database Error!")
            
            if st.button("❌ Cancel Payment"):
                st.session_state.pay_step = False
                st.rerun()
