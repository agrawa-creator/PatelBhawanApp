import streamlit as st
from supabase import create_client
import requests
import time
from datetime import datetime
import pytz  # Indian Timezone ke liye

# --- 1. CORE DATABASE CONFIG ---
URL = "https://tmwolhvzosjcegjmirrh.supabase.co"
KEY = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(URL, KEY)

# --- 2. TELEGRAM CONFIG ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_IDS = ["7261699388", "7609324930"]

def send_tele_msg(text):
    for cid in CHAT_IDS:
        try:
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          data={"chat_id": cid, "text": text, "parse_mode": "Markdown"})
        except: pass

# --- 3. SESSION & PAGE SETUP ---
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'user_info' not in st.session_state: 
    st.session_state.user_info = {"name": "", "room": "", "phone": "", "hostel": "Patel Bhavan"}

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- 4. TIME LOGIC (IST) ---
def is_late_night():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    # Raat ke 12 bje (0) se subah 6 bje tak pickup mode
    if now.hour >= 0 and now.hour < 6:
        return True
    return False

# --- 5. CLEAN DARK UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .promo-box {
        background-color: #1E2633; border-left: 5px solid #3A8DFF; 
        padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center;
    }
    .marquee-container {
        width: 100%; overflow: hidden; background: #262730;
        padding: 10px 0; border-radius: 8px; margin-bottom: 25px;
        border-bottom: 2px solid #4682B4; display: flex;
    }
    .marquee-content { display: flex; white-space: nowrap; animation: marquee 12s linear infinite; }
    .marquee-text { font-weight: bold; color: #4682B4; font-size: 17px; padding-right: 60px; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    .urgency-blink { color: #FF4B4B; font-weight: bold; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .pickup-note { background-color: #442222; border: 1px solid #FF4B4B; padding: 10px; border-radius: 5px; color: #FFD2D2; font-weight: bold; margin-bottom: 15px; }
    .mrp-text { color: #888888; text-decoration: line-through; font-size: 14px; margin-right: 8px; }
    .price-text { color: #25D366; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. TOP ANNOUNCEMENTS ---
night_mode = is_late_night()
banner_msg = "🌙 NIGHT MODE: Only Pickup from R-112 available now!" if night_mode else "🚚 Delivery Active in Patel Bhavan!"

st.markdown(f'''
    <div class="promo-box">
        <span style="color: #3A8DFF; font-weight: bold; font-size: 18px;">📢 {banner_msg}</span> 
        <br><a href="https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t" target="_blank" style="color: #25D366; text-decoration: underline; font-weight: bold;">Join Community 🔗</a>
    </div>
''', unsafe_allow_html=True)

tag_txt = "🚀 PATEL BHAVAN MART &nbsp;&nbsp; 📦 LATE NIGHT SNACKS &nbsp;&nbsp; 🛠️ ROOM 112 PICKUP &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f'<div class="marquee-container"><div class="marquee-content"><div class="marquee-text">{tag_txt * 4}</div></div></div>', unsafe_allow_html=True)

# --- 7. DATA FETCH ---
try:
    res = supabase.table("inventory").select("*").execute()
    raw_items = res.data if res.data else []
except:
    raw_items = []
    st.error("DB Error. Refresh karo.")

# --- 8. MAIN SHOP ---
st.title("🛍️ Patel Bhavan Mart")
search_query = st.text_input("🔍 Search snacks, drinks...")
selected_cat = st.segmented_control("Categories", options=["All", "Snacks", "Drinks", "Biscuits", "Others"], default="All")

col_main, col_cart = st.columns([2, 1.2])

with col_main:
    filtered = [x for x in raw_items if (not search_query or search_query.lower() in str(x.get('Name','')).lower()) and (selected_cat == "All" or x.get('Category') == selected_cat)]
    grid = st.columns(2)
    for idx, item in enumerate(filtered):
        with grid[idx % 2]:
            with st.container(border=True):
                st.image(item.get('image url', ''), use_container_width=True)
                st.subheader(item.get('Name', 'Item'))
                mrp, price, stock = item.get('MRP', 0), int(item.get('Price', 0)), int(item.get('Stock', 0))
                st.markdown(f'<div><span class="mrp-text">MRP ₹{mrp}</span><span class="price-text">Price ₹{price}</span></div>', unsafe_allow_html=True)
                if stock > 0:
                    add_qty = st.number_input(f"Qty:", min_value=1, max_value=stock, value=1, key=f"q_{item['id']}")
                    if st.button(f"🛒 Add", key=f"btn_{item['id']}"):
                        if item['Name'] in st.session_state.cart: st.session_state.cart[item['Name']]['qty'] = min(stock, st.session_state.cart[item['Name']]['qty'] + add_qty)
                        else: st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': add_qty, 'price': price, 'stock': stock}
                        st.toast(f"✅ {item['Name']} Added")
                        time.sleep(0.1)
                        st.rerun()
                else: st.error("Out of Stock")

# --- 9. CART & AUTO-PICKUP LOGIC ---
with col_cart:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart: st.info("Basket is empty!")
    else:
        total_bill = sum(info['price'] * info['qty'] for info in st.session_state.cart.values())
        order_details = ", ".join([f"{n} (x{i['qty']})" for n, i in st.session_state.cart.items()])
        for name, info in list(st.session_state.cart.items()):
            with st.expander(f"📦 {name} (x{info['qty']}) - ₹{info['price']*info['qty']}", expanded=True):
                if st.button("Remove", key=f"del_{name}"):
                    del st.session_state.cart[name]
                    st.rerun()
        st.divider()
        st.write(f"### Total: ₹{total_bill}")
        
        hostel_list = ["Patel Bhavan", "Tilak Bhavan", "Malviya Bhavan", "Other"]
        h_choice = st.selectbox("Select Your Hostel", hostel_list)
        
        # --- AUTO PICKUP LOGIC ---
        final_hostel = h_choice
        force_pickup = False
        
        if h_choice != "Patel Bhavan":
            force_pickup = True
            if h_choice == "Other": final_hostel = st.text_input("Enter Hostel Name")
            st.markdown('<div class="pickup-note">⚠️ Delivery not available in this hostel. Pickup from Patel 112.</div>', unsafe_allow_html=True)
        elif night_mode:
            force_pickup = True
            st.markdown('<div class="pickup-note">🌙 LATE NIGHT: Patel Bhavan mein bhi abhi keval Room 112 se pickup milega.</div>', unsafe_allow_html=True)
        
        c_name = st.text_input("Name", value=st.session_state.user_info['name'])
        c_room = st.text_input("Room No.", value=st.session_state.user_info['room'])
        c_phone = st.text_input("Mobile", value=st.session_state.user_info['phone'])
        
        if st.button("🚀 CONFIRM ORDER"):
            if c_name and c_room and c_phone and final_hostel:
                st.session_state.user_info = {"name": c_name, "room": c_room, "phone": c_phone, "hostel": h_choice}
                try:
                    for name, info in st.session_state.cart.items():
                        supabase.table("inventory").update({"Stock": max(0, info['stock'] - info['qty'])}).eq("id", info['id']).execute()
                    
                    order_tag = "🏠 SELF PICKUP" if force_pickup else "🚚 DELIVERY"
                    msg = f"🚀 *{order_tag}!*\n👤 {c_name}\n🏢 {final_hostel}\n📍 Room: {c_room}\n📞 {c_phone}\n📦 {order_details}\n💰 Total: ₹{total_bill}"
                    send_tele_msg(msg)
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Order Placed!")
                    time.sleep(2)
                    st.rerun()
                except: st.error("Sync Error!")
            else: st.warning("Details bharo!")
