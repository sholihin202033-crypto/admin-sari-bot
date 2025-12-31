import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS BIAR TAMPILAN CANTIK ---
st.markdown("""
<style>
    .stChatMessage {border-radius: 15px; padding: 10px;}
    .stButton button {border-radius: 20px;}
    /* Mengatur tombol + biar rapi */
    [data-testid="stPopover"] > div > button {
        border: 2px solid #eee;
        font-size: 20px;
        padding: 0px 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU SAMPING) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=100) # Ikon Sapu
    st.title("Berkilau Clean")
    st.write("Jasa kebersihan profesional: Sofa, Kasur, & Karpet.")
    
    st.divider()
    
    st.subheader("📞 Kontak Darurat")
    st.write("WA: 0857-2226-8247") # NOMOR WA BARU
    st.write("IG: @laundry.kamu") # Edit IG di sini nanti
    
    st.divider()
    
    # Tombol Reset Chat
    if st.button("🔄 Mulai Chat Baru"):
        st.session_state.messages = [] 
        st.rerun() 

# --- JUDUL UTAMA ---
st.title("✨ Chat dengan Admin Sari")
st.write("Kirim foto noda/sofa kamu, Sari akan bantu cek harganya!")

# --- KUNCI API (KONEKSI KE GOOGLE) ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Kunci API belum dipasang di Secrets!")
        st.stop()
except Exception:
    st.warning("Menunggu kunci API...")
    st.stop()

# --- SOP ADMIN & HARGA ---
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

# --- INPUT USER (TOMBOL + DAN CHAT) ---
# Kita bagi kolom: Kecil untuk tombol +, Besar untuk chat
col_plus, col_chat = st.columns([1, 8])

with col_plus:
    # Tombol Popover (Menu Muncul) dengan ikon Tambah (+)
    with st.popover("➕"):
        st.write("Lampirkan File:")
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed")

with col_chat:
    prompt = st.chat_input("Ketik pesan...")

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
    
    # Simpan ke history
    msg_content = prompt if prompt else f"[Mengirim file: {uploaded_file.name if uploaded_file else 'Foto'}]"
    st.session_state.messages.append({"role": "user", "content": msg_content})

    # 2. SIAPKAN DATA UNTUK DIKIRIM KE AI
    parts_to_send = [SOP_ADMIN]
    
    # Cek apakah file adalah gambar valid untuk AI
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            parts_to_send.append(img_data)
        except:
            # Jika file bukan gambar (misal PDF), kirim nama filenya saja ke AI
            parts_to_send.append(f"User mengirim file: {uploaded_file.name}")

    if prompt: parts_to_send.append(prompt)
    else: parts_to_send.append("Analisis gambar/file ini dan tawarkan jasa pembersihan yang cocok.")

    # 3. KIRIM KE AI (DENGAN SISTEM BAN SEREP / AUTO-FIX)
    bot_reply = ""
    with st.chat_message("assistant"):
        with st.spinner("Sari sedang mengetik..."):
            try:
                # OPSI 1: Coba pakai Mesin Utama
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(parts_to_send)
                bot_reply = response.text
            except:
                try:
                    # OPSI 2: Jika error, pakai Ban Serep
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(parts_to_send)
                    bot_reply = response.text
                except:
                    # OPSI 3: Jika masih error semua
                    bot_reply = "Maaf Kak, sistem sedang sibuk sekali. Boleh coba tanya lagi dalam 1 menit? 🙏"

            # Tampilkan Balasan
            st.write(bot_reply)
            
            # Simpan ke history
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            # --- FITUR CANGGIH: TOMBOL WA OTOMATIS ---
            # Jika AI mendeteksi kata kunci booking/jadwal/wa
            if any(x in bot_reply.lower() for x in ["jadwal", "whatsapp", "wa", "booking"]):
                st.info("👇 Klik tombol di bawah untuk lanjut ke WhatsApp Admin:")
                
                # Link WA Otomatis (NOMOR BARU)
                no_wa = "6285722268247" # SUDAH DIPERBARUI
                pesan_wa = "Halo Admin Berkilau Clean, saya mau pesan jasa cuci (dari Chatbot)."
                link = f"https://wa.me/{no_wa}?text={pesan_wa.replace(' ', '%20')}"
                
                st.link_button("📲 Lanjut Chat di WhatsApp", link) 
