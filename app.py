import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse # Untuk link WA canggih

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS VISUAL (SUPER CANTIK & RAPI) ---
st.markdown("""
<style>
    /* 1. KOTAK CHAT (INPUT) - GAYA KAPSUL */
    .stChatInput textarea {
        border-radius: 25px !important;
        padding-left: 55px !important; /* Ruang untuk tombol + */
        padding-top: 12px !important;
        border: 1px solid #ddd !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05) !important;
    }
    
    /* 2. TOMBOL (+) MENYATU DALAM KOTAK */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 28px !important;
        left: 20px !important;
        z-index: 99999 !important;
    }
    [data-testid="stPopover"] > div > button {
        background-color: transparent !important;
        border: none !important;
        color: #888 !important; /* Warna ikon abu */
        font-size: 28px !important;
        padding: 0 !important;
        transition: 0.3s;
    }
    [data-testid="stPopover"] > div > button:hover {
        color: #007bff !important; /* Biru saat disentuh */
        transform: scale(1.1); /* Efek membesar dikit */
    }

    /* 3. GELEMBUNG CHAT (CHAT BUBBLES) */
    /* User: Hijau Muda Lembut */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e8f5e9; 
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #c8e6c9;
    }
    /* Admin: Putih Bersih */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #f0f0f0;
    }

    /* 4. TOMBOL QUICK REPLY */
    .stButton button {
        border-radius: 20px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: white !important;
        color: #333 !important;
        font-size: 13px !important;
        padding: 5px 15px !important;
    }
    .stButton button:hover {
        background-color: #f5f5f5 !important;
        border-color: #bbb !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=60)
    st.title("Berkilau Clean")
    st.info("Jasa Cuci Sofa, Kasur & Karpet")
    
    st.divider()
    
    # Menu Harga Mengintip
    with st.expander("📋 Intip Daftar Harga"):
        st.markdown("""
        **Sofa:** 50rb - 60rb / dudukan
        **Kasur:** 150rb - 200rb / unit
        **Karpet:** 15rb / meter
        """)

    st.divider()
    st.write("📞 WA: 0857-2226-8247")
    st.write("IG: @laundry.kamu")
    
    if st.button("🗑️ Hapus Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- HEADER (GAMBAR SPANDUK) ---
st.image("https://img.freepik.com/free-vector/cleaning-service-banner-template_23-2148536647.jpg?w=1380", use_container_width=True)
st.subheader("👋 Halo! Sari siap bantu cek harga.")

# --- API KEY ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.stop()
except:
    st.stop()

# --- SOP ADMIN CANGGIH (SMART HANDOVER) ---
SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean'.
SIKAP: Ramah, santai, solutif, panggil 'Kak', pakai emoji (😊).

TUGAS UTAMA:
1. Jawab pertanyaan harga dan layanan DULU.
2. HANYA JIKA user bilang "Mau", "Setuju", "Booking", atau "Deal", BARU arahkan ke WhatsApp.

DATA HARGA:
- Cuci Sofa: 50rb/dudukan (Kain), 60rb/dudukan (Kulit). Min 2 dudukan.
- Cuci Kasur: 200rb (Springbed), 150rb (Latex/Busa).
- Promo: Order Senin-Rabu GRATIS Pengharum.

ATURAN DEAL (PENTING):
Jika user deal/mau booking, akhiri pesanmu dengan format rahasia ini:
"[DEAL_SUMMARY]: User mau pesan [Item] estimasi [Harga]."
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! Mau cuci apa hari ini? Boleh kirim fotonya juga ya 😊"}]

# --- TOMBOL CEPAT (QUICK REPLIES) ---
# Muncul jika chat masih kosong/baru mulai
if len(st.session_state.messages) == 1:
    st.caption("Pilihan Cepat:")
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

# --- INPUT AREA (TOMBOL + DAN CHAT MENYATU) ---
with st.popover("➕"):
    st.caption("Kirim Foto Noda:")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

prompt = st.chat_input("Ketik pesan...")

# --- PROSES UTAMA ---
if prompt or uploaded_file:
    # 1. TAMPILKAN INPUT USER
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file:
            try:
                img = Image.open(uploaded_file)
                st.image(img, width=200, caption="Foto terkirim")
            except: st.write("📁 Mengirim file...")

    # Simpan History
    txt = prompt if prompt else "[Mengirim Foto]"
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != txt:
        st.session_state.messages.append({"role": "user", "content": txt})

    # 2. PROSES AI
    parts = [SOP_ADMIN]
    if uploaded_file:
        try: parts.append(Image.open(uploaded_file))
        except: pass
    if prompt: parts.append(prompt)
    else: parts.append("Tolong analisis gambar ini dan berikan harga.")

    # 3. JAWABAN AI
    bot_reply = ""
    with st.chat_message("assistant"):
        with st.spinner("Sari sedang mengetik..."):
            try:
                # Ban Serep System (Auto-Switch Model)
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                    bot_reply = response.text
                except:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(parts)
                    bot_reply = response.text
                
                # Bersihkan kode rahasia dari tampilan
                tampilan_user = bot_reply.replace("[DEAL_SUMMARY]:", "").strip()
                st.write(tampilan_user)
                st.session_state.messages.append({"role": "assistant", "content": tampilan_user})
                
                # CEK LOGIKA HANDOVER KE WA
                if "[DEAL_SUMMARY]:" in bot_reply:
                    # Ambil ringkasan
                    ringkasan = bot_reply.split("[DEAL_SUMMARY]:")[1].strip()
                    
                    st.success("✅ Siap Kak! Data sudah Sari catat. Lanjut ke WA ya:")
                    
                    # Buat Link WA Canggih
                    no_wa = "6285722268247" # Nomor Admin
                    pesan_awal = f"Halo Admin Berkilau Clean! 👋\nSaya mau booking dari Chatbot.\n\n*Ringkasan:*\n{ringkasan}\n\nMohon info jadwal ya!"
                    pesan_encoded = urllib.parse.quote(pesan_awal)
                    link_wa = f"https://wa.me/{no_wa}?text={pesan_encoded}"
                    
                    st.link_button("📲 LANJUT KE WHATSAPP (BOOKING)", link_wa, use_container_width=True)

            except Exception as e:
                st.error("Maaf Kak, jaringan sibuk. Coba tanya lagi ya 🙏")
