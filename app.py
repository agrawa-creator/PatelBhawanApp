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
    .stButton>button { border-radius: 8px; transition: 0.3s; font-weight: bold; }
    .cart-item { background: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 5px solid #00CC66; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .delivery-tag { background: #fff3cd; color: #856404; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; }
    .shop-status-ui { font-size: 18px; font-weight: bold; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SECURE MANAGER CONTROL ---
with st.sidebar:
    st.title("🛠️ Manager Panel")
    pwd = st.text_input("Manager Password", type="password")
    
    if pwd == "Patel123":
        st.success("Access Granted! ✅")
        st.session_state.shop_open = st.toggle("Open Shop for Business", value=st.session_state.shop_open)
    
    st.divider()
    if st.session_state.shop_open:
        st.markdown("<div style='background-color:#d4edda; color:#155724;' class='shop-status-ui'>🟢 SHOP STATUS: OPEN</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color:#f8d7da; color:#721c24;' class='shop-status-ui'>🔴 SHOP STATUS: CLOSED</div>", unsafe_allow_html=True)
    st.info("Bhai, password sahi hone par hi tum shop band kar sakte ho.")

# --- HEADER & SEARCH ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛍️ Patel Bhavan Mart")
    st.caption("Premium Campus Delivery Service ⚡")
with col_h2:
    search = st.text_input("🔍 Search items...", placeholder="Oreo, Kurkure...")

# --- CATEGORY FILTER ---
cats = ["All", "Snacks", "Drinks", "Biscuits", "Others"]
selected_cat = st.segmented_control("Browse Categories", options=cats, default="All")

if not st.session_state.shop_open:
    st.warning("### 😴 Shop abhi band hai! Kal subah milte hain bhai.")
    st.stop()

# --- MAIN LAYOUT ---
col_items, col_checkout = st.columns([2, 1])

with col_items:
    try:
        db_query = supabase.table("inventory").select("*")
        if search: db_query = db_query.ilike("Name", f"%{search}%")
        if selected_cat != "All": db_query = db_query.eq("Category", selected_cat)
        
        items = db_query.execute().data
        if not items:
            st.warning("Bhai ye item toh list mein nahi hai!")
        else:
            grid = st.columns(2)
            for idx, item in enumerate(items):
                with grid[idx % 2]:
                    with st.container(border=True):
                        st.image(item.get('image url'), use_container_width=True)
                        st.subheader(item.get('Name'))
                        
                        mrp = int(item.get('MRP', 0))
                        price = int(item.get('Price', 0))
                        stock = int(item.get('Stock', 0))
                        
                        st.write(f"~~₹{mrp}~~ | **₹{price}**")
                        st.markdown("<span class='delivery-tag'>⏱️ FAST DELIVERY (5-7 MINS)</span>", unsafe_allow_html=True)
                        
                        if stock > 0:
                            st.caption(f"Stock: {stock} units left")
                            qty = st.number_input("Select Qty", 1, stock, 1, key=f"qty_{item['id']}")
                            if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                                st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': qty, 'price': price, 's': stock}
                                st.toast(f"✅ {item['Name']} added!", icon="🚀")
                                time.sleep(0.4)
                                st.rerun()
                        else:
                            st.error("Out of Stock ❌")
    except Exception as e: st.error(f"Error fetching inventory: {e}")

with col_checkout:
    st.markdown("<div style='background-color:white; padding:15px; border-radius:15px; border:1px solid #ddd;'>", unsafe_allow_html=True)
    st.subheader("🧺 Checkout Basket")
    
    if not st.session_state.cart:
        st.info("Basket khali hai bhai! Kuch add toh karo.")
    else:
        grand_total = 0
        order_list = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            grand_total += sub
            order_list += f"• {name} (x{d['qty']})\n"
            
            st.markdown(f"<div class='cart-item'><b>{name}</b><br>{d['qty']} x ₹{d['price']} = <b>₹{sub}</b></div>", unsafe_allow_html=True)
            if st.button("🗑️ Remove", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()

        st.divider()
        st.write(f"### Grand Total: ₹{grand_total}")
        st.info("💳 Pay via UPI/Cash on Delivery")
        
        # CUSTOMER DETAILS
        c_name = st.text_input("👤 Your Full Name")
        c_room = st.text_input("📍 Room No.")
        c_phone = st.text_input("📞 Mobile No.")
        
        # THE RATING SLIDER (Wapas add kar diya bhai!)
        st.write("---")
        st.write("🌟 **Rate your experience:**")
        rating = st.select_slider("How much do you like us?", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 PLACE ORDER NOW"):
            if c_name and c_room and c_phone:
                try:
                    # Update Stock in Supabase
                    for name, d in st.session_state.cart.items():
                        new_val = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_val}).eq("id", d['id']).execute()
                    
                    # Notify Telegram
                    msg = f"🔔 *NAYA ORDER AAYA HAI!*\n\n" \
                          f"👤 *Customer:* {c_name}\n" \
                          f"📍 *Room:* {c_room}\n" \
                          f"📞 *Phone:* {c_phone}\n" \
                          f"🌟 *Rating:* {rating}\n\n" \
                          f"*Items List:*\n{order_list}\n" \
                          f"💰 *Total Amount:* ₹{grand_total}\n\n" \
                          f"Bhai delivery ke liye taiyar ho jao! 🔥"
                    
                    notify(msg)
                    st.session_state.cart = {}
                    st.balloons()
                    st.success(f"Dhande ki jai ho! Order confirm ho gaya hai.")
                    time.sleep(3)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Stock update error: {ex}")
            else:
                st.warning("Bhai sari details bharna zaroori hai!")
    st.markdown("</div>", unsafe_allow_html=True)
