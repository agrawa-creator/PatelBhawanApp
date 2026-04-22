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

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- UI HEADER ---
st.title("🛍️ Patel Bhavan Mart")
st.caption("Fresh items, Delivered in minutes! 🚀")
st.markdown("---")

col_left, col_right = st.columns([2, 1])

# --- LEFT SIDE: INVENTORY ---
with col_left:
    st.subheader("📦 Select Items")
    try:
        # Fetching fresh data
        res = supabase.table("inventory").select("*").execute()
        data = res.data
        if not data:
            st.info("Stock khali hai bhai!")
        else:
            grid_cols = st.columns(2)
            for idx, item in enumerate(data):
                with grid_cols[idx % 2]:
                    # Image & Name
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    
                    p = int(item.get('Price', 0))
                    s = int(item.get('Stock', 0))
                    
                    st.write(f"**Price: ₹{p}** | Stock: {s}")
                    
                    if s > 0:
                        q = st.number_input("Select Qty", 1, s, 1, key=f"q_{item['id']}")
                        # ADD TO CART BUTTON
                        if st.button(f"➕ Add {item['Name']}", key=f"btn_{item['id']}"):
                            # 1. Update Session State
                            st.session_state.cart[item['Name']] = {
                                'id': item['id'], 
                                'qty': q, 
                                'price': p, 
                                's': s
                            }
                            # 2. SHOW POPUP (TOAST)
                            st.toast(f"✅ {item['Name']} (x{q}) Basket mein add ho gaya!", icon="🛒")
                            # 3. Small delay to let user see the popup
                            time.sleep(1) 
                            st.rerun()
                    else:
                        st.error("Out of Stock! ❌")
    except Exception as e:
        st.error(f"Error: {e}")

# --- RIGHT SIDE: CART & CHECKOUT ---
with col_right:
    st.subheader("🛒 Your Basket")
    if not st.session_state.cart:
        st.write("Basket khali hai. Kuch tasty add karo! 😋")
    else:
        total = 0
        summary = ""
        for name, details in list(st.session_state.cart.items()):
            sub = details['price'] * details['qty']
            total += sub
            st.write(f"**{name}** (x{details['qty']}) - ₹{sub}")
            summary += f"• {name} (x{details['qty']}) - ₹{sub}\n"
            if st.button("🗑️ Remove", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.markdown(f"### Total Bill: ₹{total}")
        
        # Checkout Form
        r = st.text_input("📍 Room Number", placeholder="Ex: 101")
        ph = st.text_input("📞 Mobile Number", placeholder="Ex: 9876XXXXXX")
        
        if st.button("✅ CONFIRM ORDER"):
            if r and ph:
                try:
                    # 1. Update Stock in Supabase
                    for name, d in st.session_state.cart.items():
                        new_stock = d['s'] - d['qty']
                        supabase.table("inventory").update({"Stock": new_stock}).eq("id", d['id']).execute()
                    
                    # 2. Send Notifications
                    order_msg = f"🚀 *NAYA ORDER AAYA HAI!*\n\n📍 *Room:* {r}\n📞 *Phone:* {ph}\n\n*Items List:*\n{summary}\n💰 *Total:* ₹{total}"
                    notify(order_msg)
                    
                    # 3. Clear Cart & Success Popup
                    st.session_state.cart = {}
                    st.balloons()
                    st.success("🎉 Order Booked! Dono partners ko inform kar diya gaya hai.")
                    time.sleep(3)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")
            else:
                st.warning("Bhai details toh bhar do!")
