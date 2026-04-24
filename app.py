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
        except:
            pass

# --- 3. SESSION & PAGE SETUP ---
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "room": "", "phone": "", "hostel": "Patel Bhavan"}

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
    .whatsapp-btn { 
        position: fixed; bottom: 30px; right: 30px; background-color: #25D366; 
        color: white !important; padding: 12px 25px; border-radius: 50px; 
        font-weight: bold; z-index: 1000; text-decoration: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stButton>button { border-radius: 8px; width: 100%; transition: 0.3s; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. TOP PROMO & TAGLINE ---
st.markdown("""
    <div class="promo-box">
        <span style="color: #3A8DFF; font-weight: bold; font-size: 18px;">📢 PATEL MART UPDATES:</span> 
        <br><span style="color: #E0E0E0;">Bhaiyo, naya stock aa gaya hai! Exclusive deals ke liye WhatsApp join karo.</span>
        <br><a href="https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t" target="_blank" style="color: #25D366; text-decoration: underline; font-weight: bold;">Join Community 🔗</a>
    </div>
""", unsafe_allow_html=True)

tag_txt = "🚀 FASTEST HOSTEL DELIVERY! &nbsp;&nbsp; 📦 NO MINIMUM ORDER &nbsp;&nbsp; 🍕 LATE NIGHT SNACKS &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f'<div class="marquee-container"><div class="marquee-content"><div class="marquee-text">{tag_txt * 4}</div><div class="marquee-text">{tag_txt * 4}</div></div></div>', unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager")
    pwd = st.text_input("Admin Key", type="password")
    if pwd == "Patel123":
        st.success("Authorized ✅")
        try:
            res = supabase.table("inventory").select("*").execute()
            all_items = res.data if res.data else []
            if all_items:
                sel = st.selectbox("Stock Update", [i['Name'] for i in all_items])
                val = st.number_input("Update Stock", min_value=0, step=1)
                if st.button("Save Inventory"):
                    supabase.table("inventory").update({"Stock": val}).eq("Name", sel).execute()
                    st.success("Updated!")
                    time.sleep(1)
                    st.rerun()
        except: st.error("Sidebar Error")
    st.divider()
    st.markdown("[Join WhatsApp Group](https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t)")

st.markdown('<a href="https://wa.me/918864810011" target="_blank" class="whatsapp-btn">💬 Help & Support</a>', unsafe_allow_html=True)

# --- 7. MAIN SHOP ---
st.title("🛍️ Patel Bhavan Mart")
search_query = st.text_input("🔍 Search snacks, drinks...")
cat_options = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cat_options, default="All")

col_main, col_cart = st.columns([2, 1])

with col_main:
    try:
        db_res = supabase.table("inventory").select("*").execute()
        raw_items = db_res.data if db_res.data else []
        
        filtered = raw_items
        if search_query:
            filtered = [x for x in filtered if search_query.lower() in str(x.get('Name','')).lower()]
        if selected_cat != "All":
            filtered = [x for x in filtered if x.get('Category') == selected_cat]

        if not filtered: st.info("Item nahi mila bhai!")
        
        grid = st.columns(2)
        for idx, item in enumerate(filtered):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url', ''), use_container_width=True)
                    st.subheader(item.get('Name', 'Item'))
                    p, s = int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"Price: **₹{p}** | Stock: {s}")
                    if s > 0:
                        if s <= 3: st.markdown(f"<p class='urgency-blink'>⚠️ Only {s} left!</p>", unsafe_allow_html=True)
                        if st.button(f"🛒 Add", key=f"btn_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': p, 'stock': s}
                            st.toast(f"✅ {item['Name']} added")
                            time.sleep(0.2)
                            st.rerun()
                    else: st.error("Out of Stock")
    except: st.error("Database connection issue. Refresh please.")

# --- 8. CART & CHECKOUT ---
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
            order_details += f"{name} (x1), "
            st.write(f"**{name}** - ₹{subtotal}")
            if st.button("❌ Remove", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.write(f"### Total: ₹{total_bill}")
        
        # Delivery Details
        st.subheader("📍 Delivery Address")
        # Hostel List
        hostel_list = ["Patel Bhavan", "Tilak Bhavan", "Malviya Bhavan", "Tandon Bhavan", "Other"]
        h_name = st.selectbox("Select Hostel", hostel_list)
        
        # Name/Room memory logic
        c_name = st.text_input("Name", value=st.session_state.user_info['name'])
        c_room = st.text_input("Room No.", value=st.session_state.user_info['room'])
        c_phone = st.text_input("Mobile No.", value=st.session_state.user_info['phone'])
        
        if st.button("🚀 CONFIRM ORDER"):
            if c_name and c_room and c_phone:
                # Update memory
                st.session_state.user_info = {"name": c_name, "room": c_room, "phone": c_phone, "hostel": h_name}
                
                try:
                    for name, info in st.session_state.cart.items():
                        new_s = max(0, info['stock'] - 1)
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", info['id']).execute()
                    
                    # Notify Manager (Telegram)
                    msg = f"🚀 *NEW ORDER!*\n\n👤 *Name:* {c_name}\n🏢 *Hostel:* {h_name}\n📍 *Room:* {c_room}\n📞 *Phone:* {c_phone}\n📦 *Items:* {order_details}\n💰 *Total:* ₹{total_bill}"
                    send_tele_msg(msg)
                    
                    st.session_state.cart = {}
                    st.balloons()
                    st.success(f"Order confirmed for {h_name}! Delivering in 10 mins.")
                    time.sleep(3)
                    st.rerun()
                except:
                    st.error("Error updating stock, but order sent!")
            else:
                st.warning("Please fill Name, Room, and Mobile!")
