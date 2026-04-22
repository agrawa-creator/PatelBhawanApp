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
CHAT_ID_1 = "7261699388" # Teri ID
CHAT_ID_2 = "6927591741" # Partner ki ID

def send_dual_notifications(msg):
    ids = [CHAT_ID_1, CHAT_ID_2]
    for chat_id in ids:
        f_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=Markdown"
        try: requests.get(f_url)
        except: pass

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'order_success' not in st.session_state: st.session_state.order_success = False

st.set_page_config(page_title="Patel Bhavan Mart", layout="wide", page_icon="🛒")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .cart-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #00CC66; position: sticky; top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .save-tag { color: #28a745; font-weight: bold; font-size: 12px; background: #e8f5e9; padding: 2px 8px; border-radius: 10px; }
    .mrp-text { color: #888; text-decoration: line-through; font-size: 14px; }
    .stock-low { color: #ff4b4b; font-weight: bold; font-size: 12px; }
    .stButton>button { border-radius: 10px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🛍️ Patel Bhavan Mart")
st.caption("Shared Partner Shop | Real-time Stock Management 🚀")
st.divider()

# --- SUCCESS ANIMATION ---
if st.session_state.order_success:
    st.balloons()
    st.snow()
    st.success("### 🎉 ORDER BOOKED! Dono partners ko inform kar diya hai.")
    time.sleep(4)
    st.session_state.order_success = False
    st.rerun()

# --- MAIN LAYOUT ---
col_inv, col_cart = st.columns([2, 1])

with col_inv:
    st.subheader("📦 Available Items")
    try:
        res = supabase.table("inventory").select("*").execute()
        data = res.data
        if not data:
            st.info("Stock khali hai!")
        else:
            i_cols = st.columns(2)
            for idx, item in enumerate(data):
                with i_cols[idx % 2]:
                    # Image & Name
                    st.image(item.get('image url', 'https://via.placeholder.com/200'), use_container_width=True)
                    st.markdown(f"### {item.get('Name')}")
                    
                    mrp = int(item.get('MRP', 0))
                    price = int(item.get('Price', 0))
                    stock = int(item.get('Stock', 0)) # Stock from Supabase
                    
                    # MRP & Savings
                    if mrp > price:
                        st.markdown(f"<span class='mrp-text'>MRP: ₹{mrp}</span> <span class='save-tag'>Save ₹{mrp-price}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Price: ₹{price}**")
                    
                    # Stock Logic
                    if stock <= 0:
                        st.error("Out of Stock! ❌")
                    else:
                        st.markdown(f"<span class='stock-low'>Only {stock} left in stock</span>", unsafe_allow_html=True)
                        q = st.number_input("Select Qty", 1, stock, 1, key=f"q_{idx}")
                        
                        if st.button(f"🛒 Add to Basket", key=f"add_{idx}"):
                            st.session_state.cart[item.get('Name')] = {'price': price, 'qty': q, 'max': stock}
                            st.toast(f"✅ {item.get('Name')} added!")
                            time.sleep(0.1)
                            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

with col_cart:
    st.markdown("<div class='cart-box'>", unsafe_allow_html=True)
    st.subheader("🧺 My Basket")
    
    if not st.session_state.cart:
        st.write("Basket khali hai!")
    else:
        total = 0
        summary = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total += sub
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{name}** (x{d['qty']})\n₹{sub}")
            if c2.button("🗑️", key=f"del_{name}"):
                del st.session_state.cart[name]
                st.rerun()
            summary += f"• {name} (x{d['qty']}) - ₹{sub}\n"
        
        st.divider()
        st.markdown(f"### Total Bill: ₹{total}")
        
        r = st.text_input("Room No.", placeholder="Ex: 102")
        p = st.text_input("Mobile No.", placeholder="Ex: 9876XXXXXX")
        
        if st.button("✅ CONFIRM & BOOK"):
            if r and p:
                order_msg = f"🔔 *NAYA ORDER! (Stock-Checked)*\n\n📍 *Room:* {r}\n📞 *Phone:* {p}\n\n*Items:*\n{summary}\n💰 *Total:* ₹{total}\n\n_Bhai jaldi pack kar lo!_"
                send_dual_notifications(order_msg)
                st.session_state.cart = {}
                st.session_state.order_success = True
                st.rerun()
            else:
                st.error("Room aur Phone number bharo!")
    st.markdown("</div>", unsafe_allow_html=True)
