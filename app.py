import streamlit as st
from supabase import create_client
import requests
import time

# --- CONFIG ---
# Direct credentials for stability
URL = "https://tmwolhvzosjcegjmirrh.supabase.co"
KEY = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(URL, KEY)

# --- TELEGRAM BOT DETAILS ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "7609324930"

def notify_with_buttons(msg, phone, room):
    reply_markup = {
        "inline_keyboard": [
            [{"text": "📞 Call Customer", "url": f"tel:{phone}"}],
            [
                {"text": "💰 Paid", "url": f"https://wa.me/918864810011?text=Room%20{room}%20Paid"},
                {"text": "🚚 Delivered", "url": f"https://wa.me/918864810011?text=Room%20{room}%20Delivered"}
            ]
        ]
    }
    for cid in [CHAT_ID_1, CHAT_ID_2]:
        try:
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": cid, "text": msg, "parse_mode": "Markdown", "reply_markup": reply_markup})
        except:
            pass

# --- SESSION STATE ---
if 'cart' not in st.session_state: 
    st.session_state.cart = {}

# --- PAGE CONFIG ---
st.set_page_config(page_title="Patel Bhavan Mart", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .promo-box {
        background-color: #1E2633; border-left: 5px solid #3A8DFF; 
        padding: 12px; border-radius: 8px; margin-bottom: 15px; text-align: center;
    }
    .marquee-container {
        width: 100%; overflow: hidden; background: #262730;
        padding: 10px 0; border-radius: 8px; margin-bottom: 20px;
        border-bottom: 2px solid #4682B4; display: flex;
    }
    .marquee-content { display: flex; white-space: nowrap; animation: marquee 12s linear infinite; }
    .marquee-text { font-weight: bold; color: #4682B4; font-size: 16px; padding-right: 50px; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    .urgency-blink { color: #FF4B4B; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .whatsapp-btn { 
        position: fixed; bottom: 20px; right: 20px; background-color: #25D366; 
        color: white !important; padding: 10px 20px; border-radius: 30px; 
        font-weight: bold; z-index: 1000; text-decoration: none !important;
    }
    .stButton>button { border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- TOP PROMO & TAGLINE ---
st.markdown("""
    <div class="promo-box">
        <span style="color: #3A8DFF; font-weight: bold;">📢 ANNOUNCEMENT:</span> 
        <span style="color: #E0E0E0;">Bhai, Exclusive Deals ke liye humara <b>WhatsApp Group</b> join karlo! 🔗</span>
        <br><a href="https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t" target="_blank" style="color: #25D366; text-decoration: none; font-weight: bold;">👉 Click to Join Group</a>
    </div>
""", unsafe_allow_html=True)

tag_txt = "🚀 ROOM-TO-ROOM DELIVERY ACTIVE! &nbsp;&nbsp; 📦 PATEL MART SPEED ⚡ &nbsp;&nbsp; 🍕 SNACKS & DRINKS &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f'<div class="marquee-container"><div class="marquee-content"><div class="marquee-text">{tag_txt * 4}</div><div class="marquee-text">{tag_txt * 4}</div></div></div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager")
    pwd = st.text_input("Password", type="password")
    if pwd == "Patel123":
        st.success("Authorized")
        try:
            res = supabase.table("inventory").select("*").execute()
            items = res.data if res.data else []
            if items:
                sel_name = st.selectbox("Update Stock", [i['Name'] for i in items])
                new_val = st.number_input("Stock Value", min_value=0, value=0)
                if st.button("Save Changes"):
                    supabase.table("inventory").update({"Stock": new_val}).eq("Name", sel_name).execute()
                    st.rerun()
        except:
            st.error("Access Error")
    st.divider()
    st.subheader("🔗 Links")
    st.markdown("[Join Group](https://chat.whatsapp.com/E5XZVD453tZ3nwUyqpMVNy?mode=gi_t)")

st.markdown('<a href="https://wa.me/918864810011" target="_blank" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN SHOP ---
st.title("🛍️ Patel Bhavan Mart")
search = st.text_input("🔍 Search snacks...")
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

col_inv, col_checkout = st.columns([2, 1])

with col_inv:
    try:
        # Stable data fetch
        res = supabase.table("inventory").select("*").execute()
        raw_data = res.data if res.data else []
        
        # Manual filtering to avoid Supabase query errors
        display_data = raw_data
        if search:
            display_data = [i for i in display_data if search.lower() in str(i.get('Name', '')).lower()]
        if selected_cat != "All":
            display_data = [i for i in display_data if i.get('Category') == selected_cat]

        if not display_data:
            st.info("No items available.")
        
        grid = st.columns(2)
        for idx, item in enumerate(display_data):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url', ''), use_container_width=True)
                    st.subheader(item.get('Name', 'Item'))
                    price = int(item.get('Price', 0))
                    stock = int(item.get('Stock', 0))
                    st.write(f"Price: ₹{price} | Stock: {stock}")
                    
                    if stock > 0:
                        if stock <= 3: 
                            st.markdown(f"<p class='urgency-blink'>🔥 ONLY {stock} LEFT!</p>", unsafe_allow_html=True)
                        if st.button(f"🛒 Add to Basket", key=f"btn_{item['id']}"):
                            st.session_state.cart[item['Name']] = {
                                'id': item['id'], 
                                'qty': 1, 
                                'price': price, 
                                's': stock
                            }
                            st.toast(f"✅ {item['Name']} added")
                            time.sleep(0.2)
                            st.rerun()
                    else:
                        st.error("Out of Stock")
    except Exception as e:
        st.error("Error loading inventory. Please refresh.")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart:
        st.info("Empty")
    else:
        total_bill = 0
        items_summary = ""
        for name, info in list(st.session_state.cart.items()):
            sub = info['price'] * info['qty']
            total_bill += sub
            items_summary += f"{name}, "
            st.write(f"**{name}** - ₹{sub}")
            if st.button(f"Remove", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.write(f"### Total: ₹{total_bill}")
        cust_name = st.text_input("Name")
        cust_room = st.text_input("Room No.")
        cust_phone = st.text_input("Mobile No.")
        
        if st.button("🚀 CONFIRM ORDER"):
            if cust_name and cust_room and cust_phone:
                try:
                    # Update Stock
                    for name, info in st.session_state.cart.items():
                        new_s = max(0, info['s'] - 1)
                        supabase.table("inventory").update({"Stock": new_s}).eq("id", info['id']).execute()
                    
                    # Notify Telegram
                    order_msg = f"🚀 *NEW ORDER!*\n\n👤 *User:* {cust_name}\n📍 *Room:* {cust_room}\n📞 *Phone:* {cust_phone}\n📦 *Items:* {items_summary}\n💰 *Total:* ₹{total_bill}\n\n⚠️ *STATUS: PENDING*"
                    notify_with_buttons(order_msg, cust_phone, cust_room)
                    
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Success! Order sent to Patel Mart.")
                    time.sleep(2)
                    st.rerun()
                except:
                    st.error("Connection Error. Try again.")
            else:
                st.warning("Please fill all details!")
