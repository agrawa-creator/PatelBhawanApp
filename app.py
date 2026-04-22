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
    try:
        for cid in [CHAT_ID_1, CHAT_ID_2]:
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
    except: pass

# --- SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = {}

st.set_page_config(page_title="Patel Bhawan Mart", layout="wide", page_icon="🛒")

# --- CSS UPDATES (Full Width Movement) ---
st.markdown("""
    <style>
    .stApp { background-color: #0F1116; color: #E0E0E0; }
    
    /* Full Seamless Moving Tagline */
    .marquee-container {
        width: 100%; 
        overflow: hidden; 
        background: #1E2633;
        padding: 12px 0; 
        border-radius: 8px; 
        margin-bottom: 25px;
        border-bottom: 2px solid #3A8DFF;
        display: flex;
    }

    .marquee-content { 
        display: flex; 
        white-space: nowrap; 
        /* Speed: 15s (Adjust for faster/slower movement) */
        animation: marquee 15s linear infinite; 
    }

    .marquee-text { 
        font-weight: bold; 
        color: #3A8DFF; 
        font-size: 18px; 
        padding-right: 50px; /* Space between repeated segments */
    }

    /* Animation logic for full width */
    @keyframes marquee {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    .urgency-blink {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 13px;
        animation: blinker 0.8s linear infinite;
        margin-top: 5px;
    }
    @keyframes blinker { 50% { opacity: 0; } }

    .stContainer, div[data-testid="stExpander"] {
        border: 1px solid #2D343F !important;
        background-color: #161B22 !important;
        border-radius: 12px !important;
    }

    .whatsapp-btn { 
        position: fixed; bottom: 30px; right: 30px; background-color: #2DB842; 
        color: white !important; padding: 12px 20px; border-radius: 10px; 
        font-weight: bold; z-index: 1000; text-decoration: none !important;
    }
    
    .stButton>button {
        background-color: #1E2633; color: #3A8DFF; border: 1px solid #3A8DFF;
        border-radius: 8px; width: 100%; transition: 0.2s;
    }
    .stButton>button:hover { background-color: #3A8DFF; color: white !important; }

    .cart-entry { background-color: #1C2128; border-left: 4px solid #3A8DFF; padding: 10px; border-radius: 8px; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- LONG REPEATED TEXT FOR SEAMLESS MOVEMENT ---
# Humne text ko 4 baar repeat kiya hai taaki gap na aaye
moving_text = "🚀 SUPERFAST DELIVERY ACTIVE! &nbsp;&nbsp; 📦 ROOM-TO-ROOM IN 5 MINS! &nbsp;&nbsp; ⚡ PATEL MART: THE CAMPUS LEADER! ⚡ &nbsp;&nbsp;&nbsp;&nbsp;"
st.markdown(f"""
    <div class="marquee-container">
        <div class="marquee-content">
            <div class="marquee-text">{moving_text * 4}</div>
            <div class="marquee-text">{moving_text * 4}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Manager")
    pwd = st.text_input("Password", type="password")
    if pwd == "Patel123":
        st.success("Authorized")
        try:
            items_data = supabase.table("inventory").select("*").execute().data
            sel = st.selectbox("Update Stock", [i['Name'] for i in items_data])
            curr = next(i for i in items_data if i['Name'] == sel)
            ns = st.number_input("Set Stock", value=int(curr['Stock']))
            if st.button("Save Changes"):
                supabase.table("inventory").update({"Stock": ns}).eq("Name", sel).execute()
                st.rerun()
        except: st.error("DB Connection Issue")

st.markdown('<a href="https://wa.me/918864810011" target="_blank" class="whatsapp-btn">💬 Chat Support</a>', unsafe_allow_html=True)

# --- MAIN SHOP ---
st.title("🛍️ Patel Bhavan Mart")
search = st.text_input("🔍 Search snacks...")
cats = ["All", "Snacks", "Drinks", "Biscuits", "Combos", "Others"]
selected_cat = st.segmented_control("Categories", options=cats, default="All")

col_inv, col_checkout = st.columns([2, 1])

with col_inv:
    try:
        db_query = supabase.table("inventory").select("*")
        if search: db_query = db_query.ilike("Name", f"%{search}%")
        if selected_cat != "All": db_query = db_query.eq("Category", selected_cat)
        data = db_query.execute().data
        
        grid = st.columns(2)
        for idx, item in enumerate(data or []):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(item.get('image url'), use_container_width=True)
                    st.subheader(item.get('Name'))
                    p, s = int(item.get('Price', 0)), int(item.get('Stock', 0))
                    st.write(f"Price: ₹{p} | Stock: {s}")
                    if s > 0:
                        if s <= 3: st.markdown(f"<p class='urgency-blink'>🔥 Only {s} packets left!</p>", unsafe_allow_html=True)
                        if st.button(f"🛒 Add to Basket", key=f"add_{item['id']}"):
                            st.session_state.cart[item['Name']] = {'id': item['id'], 'qty': 1, 'price': p, 's': s}
                            st.toast(f"✅ Added {item['Name']}")
                            time.sleep(0.4)
                            st.rerun()
                    else: st.error("Out of Stock")
    except Exception as e: st.error(f"Error: {e}")

with col_checkout:
    st.subheader("🧺 My Basket")
    if not st.session_state.cart: st.info("Empty")
    else:
        grand_total = 0
        order_list = ""
        for name, d in list(st.session_state.cart.items()):
            sub = d['price'] * d['qty']
            grand_total += sub
            order_list += f"• {name} (x{d['qty']})\n"
            st.markdown(f"<div class='cart-entry'><b>{name}</b><br>1 x ₹{d['price']} = ₹{sub}</div>", unsafe_allow_html=True)
            if st.button(f"Remove {name}", key=f"rm_{name}"):
                del st.session_state.cart[name]
                st.rerun()
        
        st.divider()
        st.write(f"### Total: ₹{grand_total}")
        n, r, ph = st.text_input("Name"), st.text_input("Room No."), st.text_input("Mobile No.")
        rt = st.select_slider("Rating", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        
        if st.button("🚀 CONFIRM ORDER"):
            if n and r and ph:
                for name, d in st.session_state.cart.items():
                    supabase.table("inventory").update({"Stock": d['s'] - d['qty']}).eq("id", d['id']).execute()
                notify(f"🚀 *ORDER! (8864810011)*\n\n👤 *Name:* {n}\n📍 *Room:* {r}\n📞 *Phone:* {ph}\n🌟 *Rating:* {rt}\n\n📦 *Items:*\n{order_list}\n💰 *Total:* ₹{grand_total}")
                st.session_state.cart = {}
                st.balloons()
                st.success("Success! Order placed.")
                time.sleep(2)
                st.rerun()
            else: st.warning("Details fill karo!")
