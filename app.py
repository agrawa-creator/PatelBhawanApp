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

st.set_page_config(page_title="Patel Mart | Cyber", layout="wide", page_icon="⚡")

# --- CYBERPUNK NEON CSS (The 'Wow' Factor) ---
st.markdown("""
    <style>
    /* Dark Sci-Fi Background */
    .stApp {
        background: #050505;
        color: #00FFC3;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Neon Glow Header */
    .header-text {
        text-align: center;
        color: #00FFC3;
        text-shadow: 0 0 10px #00FFC3, 0 0 20px #00FFC3;
        font-size: 50px;
        letter-spacing: 5px;
        margin-bottom: 0px;
    }

    /* Sci-Fi Product Cards */
    .card {
        background: rgba(0, 255, 195, 0.05);
        border: 1px solid #00FFC3;
        border-radius: 15px;
        padding: 20px;
        transition: 0.4s;
        box-shadow: 0 0 5px #00FFC3;
    }
    .card:hover {
        background: rgba(0, 255, 195, 0.15);
        transform: scale(1.02);
        box-shadow: 0 0 20px #00FFC3;
    }

    /* Live Ticker (News Style) */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background-color: rgba(0, 255, 195, 0.1);
        padding: 10px 0;
        border-top: 1px solid #00FFC3;
        border-bottom: 1px solid #00FFC3;
        margin-bottom: 20px;
    }
    .ticker {
        display: inline-block;
        white-space: nowrap;
        animation: ticker 30s linear infinite;
        font-weight: bold;
        color: #00FFC3;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    /* Buttons */
    .stButton>button {
        background-color: transparent;
        color: #00FFC3;
        border: 2px solid #00FFC3;
        border-radius: 5px;
        text-transform: uppercase;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00FFC3;
        color: black;
        box-shadow: 0 0 15px #00FFC3;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LIVE TICKER ---
st.markdown('<div class="ticker-wrap"><div class="ticker">🚀 ORDER UPDATE: Room 204 just grabbed a Monster Energy... 📦 STOCK ALERT: Kurkure Masala Munch running low... 🚚 DELIVERY TIME: 4 Minutes...</div></div>', unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="header-text">PATEL MART V2.0</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00FFC3; opacity:0.7;'>[ AUTHENTICATED ACCESS ONLY ]</p>", unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM SETTINGS ---
with st.sidebar:
    st.title("📟 SYSTEM CMD")
    pwd = st.text_input("Admin Key", type="password")
    if pwd == "Patel123":
        st.write("---")
        st.subheader("Inventory Override")
        # Direct stock/price editor
        items_data = supabase.table("inventory").select("*").execute().data
        for i in items_data:
            st.write(f"{i['Name']} (Qty: {i['Stock']})")
    st.divider()
    st.markdown("### 📞 ENCRYPTED CHAT")
    st.write("[WhatsApp Support Active]")

# --- GRID LAYOUT ---
col_inv, col_cart = st.columns([2, 1])

with col_inv:
    st.subheader("📂 DIGITAL INVENTORY")
    try:
        items = supabase.table("inventory").select("*").execute().data
        grid = st.columns(2)
        for idx, item in enumerate(items):
            with grid[idx % 2]:
                st.markdown(f"""
                <div class="card">
                    <img src="{item.get('image url')}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                    <h3 style="color:#00FFC3;">{item.get('Name')}</h3>
                    <p>UNIT_PRICE: ₹{item.get('Price')}</p>
                    <p style="font-size:12px; color:rgba(0,255,195,0.6);">AVAILABILITY: {item.get('Stock')} UNITS</p>
                </div>
                """, unsafe_allow_html=True)
                
                if int(item['Stock']) > 0:
                    if st.button(f"INITIATE PURCHASE #{item['id']}", key=f"btn_{item['id']}"):
                        st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': item['Price'], 's': item['Stock']}
                        st.toast("DATA_ADDED_TO_BUFFER")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.error("STATUS: UNAVAILABLE")
                st.write("")
    except Exception as e: st.error(e)

with col_checkout:
    st.subheader("🛒 DATA BUFFER")
    if not st.session_state.cart:
        st.info("BUFFER_EMPTY")
    else:
        total = 0
        order_str = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            total += sub
            order_str += f"• {name} (x{d['qty']})\n"
            st.write(f"**{name}** -> ₹{sub}")
            if st.button(f"SCRUB_{name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.markdown(f"### TOTAL_CREDITS: ₹{total}")
        n = st.text_input("IDENT_NAME")
        r = st.text_input("SECTOR_ROOM")
        
        if st.button("🚀 EXECUTE ORDER"):
            if n and r:
                # Update Stock logic
                for name, d in st.session_state.cart.items():
                    supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                
                notify(f"⚡ *SYSTEM ALERT: NEW ORDER*\nCustomer: {n}\nSector: {r}\nLoad:\n{order_str}\nCredits: ₹{total}")
                st.session_state.cart = {}
                st.balloons()
                st.success("TRANSACTION_COMPLETE")
                time.sleep(2)
                st.rerun()
