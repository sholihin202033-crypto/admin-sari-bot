import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS KHUSUS (GEMINI STYLE) ---
# Ini rahasianya agar tampilan jadi bulat/lonjong seperti aplikasi HP
st.markdown("""
<style>
    /* 1. Mengubah kotak ketik (Chat Input) jadi Lonjong/Kapsul */
    .stChatInput textarea {
        border-radius: 25px !important; /* Membuat sudut tumpul */
        border: 1px solid #c0c0c0; /* Garis pinggir halus */
        padding-left: 20px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    /* 2. Mengubah tombol kirim (Send) jadi lebih pas */
    .stChatInput button {
        border-radius: 50%;
    }

    /* 3. Mengubah Tombol Tambah (+) jadi Bulat Sempurna */
    [data-testid="stPopover"] > div > button {
        border-radius: 50% !important; /* Lingkaran penuh */
        width: 50px;
        height: 50px;
        border: 1px solid #ddd;
        background-color: #f0f2f6;
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 8px; /* Supaya sejajar dengan kotak chat */
    }

    /* Menghilangkan border fokus biru yang jelek */
    .stChatInput textarea:focus {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 5px rgba(76, 175, 80, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU SAMPING) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=100)
    st.title("Berkilau Clean")
    st.write("Jasa kebersihan profesional: Sofa, Kasur, & Karpet.")
    
    st.divider()
    
    st.subheader("📞 Kontak Darurat")
    st.write("WA: 0857-2226-8247")
    st.write("IG: @laundry.kamu")
    
    st.divider()
    
    if st.button("🔄 Mulai Chat Baru"):
        st.session_state.messages = [] 
        st.rerun() 

# --- JUDUL UTAMA ---
st.title("✨ Chat dengan Admin Sari")
st.write("Sari siap bantu cek harga & jadwal!")

# --- KUNCI API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Kunci API belum dipasang di Secrets!")
        st.stop()
except Exception:
    st.warning("Menunggu kunci API...")
    st.stop()

# --- SOP ADMIN ---
SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean'.
SIKAP: Ramah, santai, solutif, panggil 'Kak', pakai emoji (😊).
TUJUAN: Menganalisis masalah kebersihan user & mengarahkan mereka untuk BOOKING via WhatsApp.

DATA HARGA:
1. CUCI SOFA: 
   - Standar: 50rb/dkk.
   - Khusus (Kulit/Beludru): 60rb/dkk.
   - Min order 2 dudukan.
2. CUCI KASUR: 
   - Springbed: 200rb (Semua ukuran).
   - Latex: 150rb.
3. PROMO: Booking Senin-Rabu GRATIS 1 Pengharum Ruangan.

INSTRUKSI KHUSUS:
- Jika user mengirim GAMBAR: Komentari noda/kondisinya.
- Jika user bertanya harga, jawab sesuai data.
- Jika user deal, arahkan KLIK TOMBOL WHATSAPP.
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo Kak! Saya Sari. Ada yang bisa dibantu? Boleh kirim foto sofanya biar saya cek ya 😊"}
    ]

# TAMPILKAN CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT USER (GAYA GEMINI: TOMBOL BULAT + KOTAK LONJONG) ---
# Kita atur kolom agar tombol + ada di kiri kotak chat
col_plus, col_chat = st.columns([1, 12]) 

with col_plus:
    # Tombol + Bulat
    with st.popover("➕"):
        st.write("Lampirkan File:")
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed")

with col_chat:
    # Kotak Chat (Akan jadi lonjong karena CSS di atas)
    prompt = st.chat_input("Ketik pesan atau tanya harga...")

# --- PROSES CHAT ---
if prompt or uploaded_file:
    # 1. Tampilkan Pesan User
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file: 
            try:
                img = Image.open(uploaded_file)
                st.image(img, caption="Foto dikirim", width=250)
            except:
                st.write(f"📄 Mengirim file: {uploaded_file.name}")
    
    # Simpan history
    msg_content = prompt if prompt else f"[Mengirim file: {uploaded_file.name if uploaded_file else 'Foto'}]"
    st.session_state.messages.append({"role": "user", "content": msg_content})

    # 2. Siapkan Data
    parts_to_send = [SOP_ADMIN]
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            parts_to_send.append(img_data)
        except:
            parts_to_send.append(f"User mengirim file: {uploaded_file.name}")
    
    if prompt: parts_to_send.append(prompt)
    else: parts_to_send.append("Analisis gambar/file ini.")

    # 3. Kirim ke AI (Anti-Error System)
    bot_reply = ""
    with st.chat_message("assistant"):
        with st.spinner("Sari sedang mengetik..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(parts_to_send)
                bot_reply = response.text
            except:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(parts_to_send)
                    bot_reply = response.text
                except:
                    bot_reply = "Maaf Kak, sistem sibuk. Coba lagi ya 🙏"

            st.write(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            # Tombol WA Otomatis
            if any(x in bot_reply.lower() for x in ["jadwal", "whatsapp", "wa", "booking"]):
                st.info("👇 Klik tombol untuk lanjut ke WhatsApp:")
                no_wa = "6285722268247"
                pesan_wa = "Halo Admin Berkilau Clean, mau pesan jasa cuci (dari Chatbot)."
                link = f"https://wa.me/{no_wa}?text={pesan_wa.replace(' ', '%20')}"
                st.link_button("📲 Lanjut ke WhatsApp", link) 
