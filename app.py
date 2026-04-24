import streamlit as st
from supabase import create_client
import requests
import time

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

# --- 4. CLEAN DARK UI ---
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

# --- 5. TOP ANNOUNCEMENTS ---
st.markdown('<div class="promo-box"><span style="color: #3A8DFF; font-weight: bold; font-size: 18px;">📢 PATEL MART UPDATES:</span><br><span style="color: #E0E0E0;">Bhaiyo, Exclusive deals ke liye WhatsApp join karo.</span><br><a href="https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t" target="_blank" style="color: #25D366; text-decoration: underline; font-weight: bold;">Join Community 🔗</a></div>', unsafe_allow_html=True)

tag_txt = "🚀 PATEL BHAVAN DELIVERY ONLY! &nbsp;&nbsp; 📦 OTHERS PICKUP FROM ROOM 112 &nbsp;&nbsp; 🍕 LATE NIGHT SNACKS &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f'<div class="marquee-container"><div class="marquee-content"><div class="marquee-text">{tag_txt * 4}</div></div></div>', unsafe_allow_html=True)

# --- 6. DATA FETCH ---
try:
    res = supabase.table("inventory").select("*").execute()
    raw_items = res.data if res.data else []
except:
    raw_items = []
    st.error("Database connection issue. Refresh please.")

# --- 7. MAIN SHOP LOGIC ---
st.title("🛍️ Patel Bhavan Mart")
search_query = st.text_input("🔍 Search snacks, drinks...")
cat_options = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cat_options, default="All")

col_main, col_cart = st.columns([2, 1.2])

with col_main:
    filtered = raw_items
    if search_query:
        filtered = [x for x in filtered if search_query.lower() in str(x.get('Name','')).lower()]
    if selected_cat and selected_cat != "All":
        filtered = [x for x in filtered if x.get('Category') == selected_cat]

    grid = st.columns(2)
    for idx, item in enumerate(filtered):
        with grid[idx % 2]:
            with st.container(border=True):
                st.image(item.get('image url', ''), use_container_width=True)
                st.subheader(item.get('Name', 'Item'))
                
                mrp = item.get('MRP', 0)
                price = int(item.get('Price', 0))
                stock = int(item.get('Stock', 0))
                
                st.markdown(f'<div><span class="mrp-text">MRP ₹{mrp}</span><span class="price-text">Price ₹{price}</span></div>', unsafe_allow_html=True)
                
                if stock > 0:
                    add_qty = st.number_input(f"Qty:", min_value=1, max_value=stock, value=1, key=f"qty_in_{item['id']}")
                    if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                        if item['Name'] in st.session_state.cart:
                            st.session_state.cart[item['Name']]['qty'] = min(stock, st.session_state.cart[item['Name']]['qty'] + add_qty)
                        else:
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': add_qty, 'price': price, 'stock': stock}
                        st.toast(f"✅ Added {item['Name']}")
                        time.sleep(0.1)
                        st.rerun()
                else: st.error("Out of Stock")

# --- 8. CART & PICKUP LOGIC ---
with col_cart:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart:
        st.info("Basket is empty!")
    else:
        total_bill = 0
        order_details = ""
        for name, info in list(st.session_state.cart.items()):
            subtotal = info['price'] * info['qty']
            total_bill += subtotal
            order_details += f"{name} (x{info['qty']}), "
            with st.expander(f"📦 {name} (x{info['qty']}) - ₹{subtotal}", expanded=True):
                if st.button(f"Remove Item", key=f"del_{name}"):
                    del st.session_state.cart[name]
                    st.rerun()

        st.divider()
        st.write(f"### Total Bill: ₹{total_bill}")
        
        # Address Details
        hostel_list = ["Patel Bhavan", "Tilak Bhavan", "Malviya Bhavan", "Other"]
        h_choice = st.selectbox("Select Your Hostel", hostel_list)
        
        # PICKUP LOGIC
        is_pickup = False
        final_hostel = h_choice
        if h_choice != "Patel Bhavan":
            is_pickup = True
            if h_choice == "Other":
                final_hostel = st.text_input("Hostel Ka Naam Likhein")
            st.markdown('<div class="pickup-note">⚠️ Note: Is hostel mein delivery band hai. Order confirm karke Patel Bhavan, Room 112 se pickup kar lo.</div>', unsafe_allow_html=True)
        
        c_name = st.text_input("Name", value=st.session_state.user_info['name'])
        c_room = st.text_input("Room No.", value=st.session_state.user_info['room'])
        c_phone = st.text_input("Mobile No.", value=st.session_state.user_info['phone'])
        
        if st.button("🚀 CONFIRM ORDER"):
            if c_name and c_room and c_phone and final_hostel:
                st.session_state.user_info = {"name": c_name, "room": c_room, "phone": c_phone, "hostel": h_choice}
                try:
                    for name, info in st.session_state.cart.items():
                        new_s = max(0, info['stock'] - info['qty'])
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", info['id']).execute()
                    
                    order_type = "🏠 SELF PICKUP (R-112)" if is_pickup else "🚚 HOME DELIVERY"
                    msg = f"🚀 *{order_type}!*\n\n👤 *Name:* {c_name}\n🏢 *Hostel:* {final_hostel}\n📍 *Room:* {c_room}\n📞 *Phone:* {c_phone}\n📦 *Items:* {order_details}\n💰 *Total:* ₹{total_bill}"
                    send_tele_msg(msg)
                    
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Order Placed Successfully!")
                    time.sleep(3)
                    st.rerun()
                except: st.error("Error! But order sent to manager.")
            else: st.warning("Saari details bharo bhai!")
