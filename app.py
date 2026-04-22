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

st.set_page_config(page_title="Patel Bhavan Mart | Pro", layout="wide", page_icon="🛍️")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stSearchInput { border-radius: 20px; }
    .status-open { color: #28a745; font-weight: bold; font-size: 18px; }
    .status-closed { color: #dc3545; font-weight: bold; font-size: 18px; }
    .delivery-tag { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .cart-box { background: white; padding: 20px; border-radius: 15px; border-top: 5px solid #00CC66; box-shadow: 0 4px 15px rgba(0,0,0,0.1); position: sticky; top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: MANAGER CONTROLS ---
with st.sidebar:
    st.header("⚙️ Manager Panel")
    st.session_state.shop_open = st.toggle("Shop Status (Open/Closed)", value=st.session_state.shop_open)
    if st.session_state.shop_open:
        st.markdown("<p class='status-open'>🟢 WE ARE OPEN</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p class='status-closed'>🔴 WE ARE CLOSED</p>", unsafe_allow_html=True)
    st.divider()
    st.info("Bhai, yahan se tum shop band kar sakte ho jab sone jao ya class mein ho.")

# --- HEADER & SEARCH ---
t1, t2 = st.columns([3, 1])
with t1:
    st.title("🛍️ Patel Bhavan Mart")
    st.caption("Hostel's Most Professional Store | Quality & Speed 🚀")
with t2:
    search_query = st.text_input("🔍 Search snacks...", placeholder="Lays, Oreo...")

# --- CATEGORY FILTER ---
categories = ["All", "Snacks", "Drinks", "Biscuits", "Essentials"]
selected_cat = st.segmented_control("Filter by Category", categories, default="All")

st.divider()

if not st.session_state.shop_open:
    st.error("### 😴 Shop abhi band hai bhai! Thoda intezaar karo ya kal aana.")
    st.stop()

# --- MAIN LAYOUT ---
col_inv, col_cart = st.columns([2, 1])

with col_inv:
    try:
        # Fetch Data
        query = supabase.table("inventory").select("*")
        # Search Filter Logic
        if search_query:
            query = query.ilike("Name", f"%{search_query}%")
        # Category Filter Logic
        if selected_cat != "All":
            query = query.eq("Category", selected_cat)
            
        data = query.execute().data
        
        if not data:
            st.warning("Koi saaman nahi mila bhai!")
        else:
            i_cols = st.columns(2)
            for idx, item in enumerate(data):
                with i_cols[idx % 2]:
                    with st.container(border=True):
                        st.image(item.get('image url'), use_container_width=True)
                        st.subheader(item.get('Name'))
                        
                        mrp, price = int(item.get('MRP', 0)), int(item.get('Price', 0))
                        stock = int(item.get('Stock', 0))
                        
                        c1, c2 = st.columns(2)
                        c1.write(f"~~₹{mrp}~~ **₹{price}**")
                        c2.markdown("<span class='delivery-tag'>⏱️ 5-7 MINS</span>", unsafe_allow_html=True)
                        
                        if stock > 0:
                            st.write(f"✅ In Stock: {stock}")
                            q = st.number_input("Qty", 1, stock, 1, key=f"q_{item['id']}")
                            if st.button(f"🛒 Add to Basket", key=f"btn_{item['id']}"):
                                st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': q, 'price': price, 's': stock}
                                st.toast(f"✅ {item['Name']} added!", icon="🚀")
                                time.sleep(0.5)
                                st.rerun()
                        else:
                            st.error("Out of Stock ❌")
    except Exception as e: st.error(f"Error: {e}")

# --- CART & CHECKOUT ---
with col_cart:
    st.markdown("<div class='cart-box'>", unsafe_allow_html=True)
    st.subheader("🧺 Your Order")
    
    if not st.session_state.cart:
        st.write("Basket khali hai!")
    else:
        total = 0
        summary = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total += sub
            st.write(f"**{name}** (x{d['qty']}) - ₹{sub}")
            summary += f"• {name} (x{d['qty']})\n"
            if st.button("🗑️", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.write(f"### Total: ₹{total}")
        
        # QR Placeholder
        st.info("💳 Pay via UPI on delivery or scan QR at room.")
        
        room = st.text_input("📍 Room No.")
        phone = st.text_input("📞 Phone No.")
        
        # Rating Feature (Point 6)
        rating = st.select_slider("Rate our service", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        
        if st.button("🚀 CONFIRM & DELIVER"):
            if room and phone:
                try:
                    # Update Stock
                    for name, d in st.session_state.cart.items():
                        supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                    
                    # Notify Managers
                    msg = f"🔔 *NEW ORDER!*\nRoom: {room}\nPhone: {phone}\nItems:\n{summary}\nTotal: ₹{total}\nRating: {rating}"
                    notify(msg)
                    
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("Bhai order mil gaya! 5 min mein pahunch rahe hain.")
                    time.sleep(3)
                    st.rerun()
                except: st.error("Stock update fail! Check RLS.")
            else:
                st.error("Room aur Phone number daalo!")
    st.markdown("</div>", unsafe_allow_html=True)
