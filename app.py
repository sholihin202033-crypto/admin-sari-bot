import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS "CANTIK & MODERN" ---
st.markdown("""
<style>
    /* 1. KOTAK CHAT (INPUT) - GAYA WHATSAPP */
    .stChatInput textarea {
        border-radius: 25px !important;
        padding-left: 50px !important; 
        padding-top: 12px !important;
        border: 1px solid #ddd !important;
    }

    /* 2. TOMBOL (+) DI DALAM KOTAK */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 28px !important;
        left: 18px !important;
        z-index: 99999 !important;
    }
    [data-testid="stPopover"] > div > button {
        background-color: transparent !important;
        border: none !important;
        color: #888 !important;
        font-size: 28px !important;
        padding: 0 !important;
    }
    [data-testid="stPopover"] > div > button:hover {
        color: #007bff !important; /* Warna biru saat disentuh */
    }

    /* 3. TOMBOL "QUICK REPLY" (PILIHAN CEPAT) */
    .stButton button {
        border-radius: 20px !important;
        border: 1px solid #eee !important;
        background-color: #f8f9fa !important;
        color: #333 !important;
        font-size: 14px !important;
        padding: 5px 15px !important;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #e2e6ea !important;
        border-color: #adb5bd !important;
    }

    /* 4. HEADER RAPI */
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 16px;
        color: #7f8c8d;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU) ---
with st.sidebar:
    st.title("Berkilau Clean ✨")
    st.info("Jasa Cuci Sofa, Kasur & Karpet (Home Service)")
    
    st.divider()
    
    # Menu Harga Mengintip (Accordion)
    with st.expander("📋 Lihat Daftar Harga"):
        st.markdown("""
        **Sofa:**
        - Kain: 50rb/dudukan
        - Kulit: 60rb/dudukan
        
        **Kasur:**
        - Single: 150rb
        - Queen/King: 200rb
        
        **Karpet:**
        - Permeter: 15rb
        """)

    st.divider()
    st.write("📞 WA: 0857-2226-8247")
    st.write("IG: @laundry.kamu")
    
    if st.button("🗑️ Hapus Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- BAGIAN UTAMA ---

# Header Cantik (Bisa ganti URL gambar spanduk sendiri nanti)
st.image("https://img.freepik.com/free-vector/cleaning-service-banner-template_23-2148536647.jpg?w=1380", use_container_width=True)

st.markdown('<div class="main-header">Halo! Sari di sini 👋</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Asisten pintar yang siap bantu cek harga & jadwal cuci.</div>', unsafe_allow_html=True)

# --- API KEY ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.stop()
except:
    st.stop()

# --- SOP ADMIN ---
SOP_ADMIN = """
PERAN: Kamu Admin Sari (Berkilau Clean).
SIKAP: Ramah, santai, pakai emoji 😊.
HARGA:
- Sofa: 50rb/dudukan.
- Kasur Springbed: 200rb.
TUJUAN: Jawab harga & arahkan ke WhatsApp.
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! Mau dibantu cuci apa hari ini? 😊"}]

# --- FITUR TOMBOL CEPAT (QUICK REPLIES) ---
# Ini agar customer tidak capek ngetik
if len(st.session_state.messages) == 1: # Hanya muncul di awal chat
    st.write("Pilihan Cepat:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛋️ Cuci Sofa"):
            st.session_state.messages.append({"role": "user", "content": "Berapa harga cuci sofa?"})
            st.rerun()
    with col2:
        if st.button("🛏️ Cuci Kasur"):
            st.session_state.messages.append({"role": "user", "content": "Berapa harga cuci kasur?"})
            st.rerun()
    with col3:
        if st.button("📍 Lokasi"):
            st.session_state.messages.append({"role": "user", "content": "Melayani area mana saja?"})
            st.rerun()

# TAMPILKAN HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

st.write("") 
st.write("") 

# --- INPUT CHAT & TOMBOL (+) MENYATU ---
with st.popover("➕"):
    st.caption("Upload Foto Noda:")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

prompt = st.chat_input("Ketik pesan...")

# --- LOGIKA ---
if prompt or uploaded_file:
    # USER INPUT
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file:
            try:
                img = Image.open(uploaded_file)
                st.image(img, width=200)
            except: st.write(f"📁 File")

    # SIMPAN HISTORY
    txt = prompt if prompt else "[Kirim Foto]"
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != txt:
        st.session_state.messages.append({"role": "user", "content": txt})

    # AI PROCESS
    parts = [SOP_ADMIN]
    if uploaded_file:
        try: parts.append(Image.open(uploaded_file))
        except: pass
    if prompt: parts.append(prompt)
    else: parts.append("Analisis ini.")

    # AI REPLY
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                    reply = response.text
                except:
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(parts)
                        reply = response.text
                    except:
                        reply = "Maaf Kak, jaringan sibuk. Coba lagi ya 🙏"
                
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                if "wa" in reply.lower() or "booking" in reply.lower():
                    link = "https://wa.me/6285722268247?text=Halo%20Admin%20Berkilau"
                    st.link_button("📲 Chat WhatsApp (Booking)", link, use_container_width=True)
