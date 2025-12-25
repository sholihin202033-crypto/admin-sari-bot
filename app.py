import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS BIAR TAMPILAN CANTIK (Opsional) ---
st.markdown("""
<style>
    .stChatMessage {border-radius: 15px; padding: 10px;}
    .stButton button {width: 100%; border-radius: 20px;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU SAMPING) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=100) # Ikon Sapu
    st.title("Berkilau Clean")
    st.write("Jasa kebersihan profesional: Sofa, Kasur, & Karpet.")
    
    st.divider()
    
    st.subheader("📞 Kontak Darurat")
    st.write("WA: 0812-3456-7890")
    st.write("IG: @berkilau.clean")
    
    st.divider()
    
    # Tombol Reset Chat
    if st.button("🔄 Mulai Chat Baru"):
        st.session_state.messages = [] # Kosongkan memori
        st.rerun() # Refresh halaman

# --- LOGIKA UTAMA ---
st.title("✨ Chat dengan Admin Sari")
st.write("Kirim foto noda/sofa kamu, Sari akan bantu cek harganya!")

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

# --- SOP ADMIN & HARGA (DIPERTAJAM) ---
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
- Jika user mengirim GAMBAR: Komentari noda/kondisinya. Contoh: "Wah, nodanya cukup dalam ya Kak, tapi tenang bisa kami atasi dengan Deep Cleaning."
- Jika user bertanya harga, jawab sesuai data di atas.
- Jika user setuju/tertarik, arahkan untuk KLIK TOMBOL WHATSAPP di bawah (jangan minta nomor WA manual).
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

# --- INPUT USER (GAMBAR & TEKS) ---
# Wadah input
col1, col2 = st.columns([1, 4])
with col1:
    with st.popover("📸 Upload Foto"):
        uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"])

with col2:
    prompt = st.chat_input("Ketik pesan...")

# --- PROSES CHAT ---
if prompt or uploaded_file:
    # 1. Tampilkan Pesan User
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file: 
            img = Image.open(uploaded_file)
            st.image(img, caption="Foto dikirim", width=250)
    
    # Simpan ke history
    msg_content = prompt if prompt else "[Mengirim foto]"
    st.session_state.messages.append({"role": "user", "content": msg_content})

    # 2. Kirim ke AI
    try:
        # Gunakan model Gemini 2.5 Flash (Sesuai diagnosa tadi)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        parts_to_send = [SOP_ADMIN]
        if uploaded_file: parts_to_send.append(Image.open(uploaded_file))
        if prompt: parts_to_send.append(prompt)
        else: parts_to_send.append("Analisis gambar ini dan tawarkan jasa pembersihan yang cocok.")

        with st.spinner("Sari sedang mengetik..."):
            response = model.generate_content(parts_to_send)
        
        bot_reply = response.text
        
        # 3. Tampilkan Balasan AI
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
            
            # --- FITUR TOMBOL WA OTOMATIS (CANGGIH) ---
            # Jika AI mendeteksi user mau order, kita munculkan tombol
            if "jadwal" in bot_reply.lower() or "whatsapp" in bot_reply.lower() or "wa" in bot_reply.lower():
                st.info("👇 Klik tombol di bawah untuk lanjut ke WhatsApp Admin:")
                
                # Link WA Otomatis
                no_wa = "6281234567890" # GANTI NOMOR INI
                pesan_wa = "Halo Admin Berkilau Clean, saya mau pesan jasa cuci (dari Chatbot)."
                link = f"https://wa.me/{no_wa}?text={pesan_wa.replace(' ', '%20')}"
                
                st.link_button("📲 Lanjut Chat di WhatsApp", link)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
