import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari Vision", page_icon="✨")
st.title("✨ Admin Sari - Berkilau Clean")
st.write("Silakan tanya harga, layanan, atau kirim foto sofa/kasur kotor untuk dicek!")

# --- KUNCI API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Kunci API belum dipasang di Secrets!")
        st.stop()
except Exception:
    st.warning("Menunggu konfigurasi API...")
    st.stop()

# --- SOP ADMIN & HARGA ---
SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean'.
SIKAP: Ramah, santai, solutif, panggil pelanggan dengan 'Kak' dan gunakan emoji (😊, 👍, 🙏).

INSTRUKSI ANALISIS GAMBAR:
- Jika user mengirim gambar, perhatikan kondisinya (noda, jenis bahan, atau tingkat kekotoran).
- Berikan komentar empati seperti "Waduh, nodanya lumayan terlihat ya Kak" atau "Wah, ini bahan beludru ya Kak, butuh penanganan khusus."
- Hubungkan kondisi gambar dengan layanan yang sesuai.

DATA HARGA:
1. CUCI SOFA: Standar 50rb/dkk, Khusus (Kulit/Beludru) 60rb/dkk. Min order 2.
2. CUCI KASUR: Springbed 200rb, Latex 150rb.
3. PROMO: Booking Senin-Rabu GRATIS 1 Pengharum Ruangan.

ATURAN CHAT:
- Akhiri dengan tawaran: "Apakah Kakak mau langsung dijadwalkan?"
- Minta data alamat & WA jika deal.
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hai Kak! Saya Sari. Ada yang bisa saya bantu? Kalau ada foto sofa/kasur kotor, kirim saja ya 😊"}
    ]

# TAMPILKAN CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT USER (GAMBAR & TEKS) ---
with st.expander("📸 Klik di sini untuk Upload Foto (Opsional)", expanded=False):
    uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"])

prompt = st.chat_input("Ketik pesanmu di sini...")

if prompt or uploaded_file:
    # Tampilkan pesan user
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file: 
            img = Image.open(uploaded_file)
            st.image(img, caption="Foto dikirim", width=250)
            st.write("(Mengirim foto...)")
    
    # Simpan ke history (teks saja biar ringan)
    msg_content = prompt if prompt else "[Mengirim foto]"
    st.session_state.messages.append({"role": "user", "content": msg_content})

    # Kirim ke AI
    try:
        # --- PERBAIKAN: Menggunakan Model Gemini 2.5 Flash sesuai akun Kakak ---
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Susun pesan untuk AI (Gabungan Text History + Gambar Baru)
        parts_to_send = [SOP_ADMIN]
        
        # Masukkan Gambar (Jika ada)
        if uploaded_file:
            parts_to_send.append(Image.open(uploaded_file))
            
        # Masukkan Pertanyaan User
        if prompt:
            parts_to_send.append(prompt)
        else:
            parts_to_send.append("Tolong analisis gambar ini sesuai SOP layanan kebersihan kita.")

        # Kirim
        with st.spinner("Sari sedang menganalisis..."):
            response = model.generate_content(parts_to_send)
        
        # Balasan AI
        bot_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
