import streamlit as st
from supabase import create_client
import requests
import time

# --- CONFIG ---
url = "https://tmwolhvzosjcegjmirrh.supabase.co"
key = "sb_publishable_RQuXJ1BP3wpLnWmp3WLMvQ_vT5mxYq4"
supabase = create_client(url, key)

# --- DUAL TELEGRAM SETTINGS ---
TELE_TOKEN = "7954541566:AAFdSIYkxCp1KYCZN3CFhj5Fd8TU89X6whs"
CHAT_ID_1 = "7261699388"
CHAT_ID_2 = "7609324930"

def send_dual_notifications(msg):
    ids = [CHAT_ID_1, CHAT_ID_2]
    for chat_id in ids:
        f_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        try:
            requests.post(f_url, data=payload)
        except:
            pass

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'order_success' not in st.session_state: st.session_state.order_success = False

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- CSS ---
st.markdown("""
    <style>
    .cart-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #00CC66; position: sticky; top: 10px; }
    .save-tag { color: #28a745; font-weight: bold; font-size: 12px; background: #e8f5e9; padding: 2px 8px; border-radius: 10px; }
    .mrp-text { color: #888; text-decoration: line-through; font-size: 14px; }
    .stock-low { color: #ff4b4b; font-weight: bold; font-size: 12px; }
    .stButton>button { border-radius: 10px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛍️ Patel Bhavan Mart")
st.caption("Live Inventory Sync Enabled 🚀")
st.divider()

if st.session_state.order_success:
    st.balloons()
    st.success("### 🎉 ORDER PLACED! Stock Updated successfully.")
    time.sleep(2)
    st.session_state.order_success = False
    st.rerun()

col_inv, col_cart = st.columns([2, 1])

with col_inv:
    st.subheader("📦 Menu")
    try:
        # Fetching fresh data every time
        res = supabase.table("inventory").select("*").execute()
        data = res.data
        if not data:
            st.info("Stock khali hai!")
        else:
            i_cols = st.columns(2)
            for idx, item in enumerate(data):
                with i_cols[idx % 2]:
                    st.image(item.get('image url', 'https://via.placeholder.com/200'), use_container_width=True)
                    st.markdown(f"### {item.get('Name')}")
                    
                    mrp = int(item.get('MRP', 0))
                    price = int(item.get('Price', 0))
                    stock = int(item.get('Stock', 0))
                    item_id = item.get('id') # Unique ID for update
                    
                    if mrp > price:
                        st.markdown(f"<span class='mrp-text'>MRP: ₹{mrp}</span> <span class='save-tag'>Save ₹{mrp-price}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Price: ₹{price}**")
                    
                    if stock <= 0:
                        st.error("Out of Stock! ❌")
                    else:
                        st.markdown(f"<span class='stock-low'>Stock available: {stock}</span>", unsafe_allow_html=True)
                        q = st.number_input("Qty", 1, stock, 1, key=f"q_{idx}")
                        if st.button(f"🛒 Add to Basket", key=f"add_{idx}"):
                            # Storing item ID and stock info in cart
                            st.session_state.cart[item.get('Name')] = {
                                'price': price, 
                                'qty': q, 
                                'id': item_id, 
                                'current_stock': stock
                            }
                            st.toast(f"✅ {item.get('Name')} added!")
                            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

with col_cart:
    st.markdown("<div class='cart-box'>", unsafe_allow_html=True)
    st.subheader("🧺 Basket")
    
    if not st.session_state.cart:
        st.write("Basket khali hai!")
    else:
        total = 0
        summary = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total += sub
            st.write(f"**{name}** (x{d['qty']}) - ₹{sub}")
            summary += f"• {name} (x{d['qty']}) - ₹{sub}\n"
            if st.button("🗑️", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.markdown(f"### Total: ₹{total}")
        r = st.text_input("Room No.")
        p = st.text_input("Phone No.")
        
        if st.button("✅ CONFIRM & BOOK"):
            if r and p:
                try:
                    # 1. Update Stock in Supabase using ID
                    for name, d in st.session_state.cart.items():
                        new_stock = d['current_stock'] - d['qty']
                        # Updating by ID is 100% accurate
                        supabase.table("inventory").update({"Stock": new_stock}).eq("id", d['id']).execute()
                    
                    # 2. Send Telegram
                    order_msg = f"🚀 *ORDER PLACED!*\n\n📍 *Room:* {r}\n📞 *Phone:* {p}\n\n*Items:*\n{summary}\n💰 *Total:* ₹{total}"
                    send_dual_notifications(order_msg)
                    
                    # 3. Clear Cart and Show Success
                    st.session_state.cart = {}
                    st.session_state.order_success = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Stock Update Error: {e}")
            else:
                st.error("Room aur Phone number bharo!")
    st.markdown("</div>", unsafe_allow_html=True)
