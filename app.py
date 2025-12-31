import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS TAMPILAN (GEMINI STYLE - VERSI RAPI) ---
st.markdown("""
<style>
    /* 1. Merapikan Kotak Chat jadi Lonjong (Kapsul) */
    .stChatInput textarea {
        border-radius: 25px !important;
        border: 1px solid #e0e0e0 !important; /* Garis abu halus */
        padding-left: 15px;
    }
    
    /* 2. Menghilangkan fokus warna aneh */
    .stChatInput textarea:focus {
        border-color: #777 !important;
        box-shadow: none !important;
    }

    /* 3. Merapikan tampilan pesan chat */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU & UPLOAD) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=80) 
    st.title("Berkilau Clean")
    st.write("Jasa kebersihan profesional.")
    
    st.divider()
    
    # --- FITUR UPLOAD (DIPINDAH KE SINI BIAR RAPI) ---
    st.subheader("📸 Kirim Foto Noda")
    st.info("Mau cek harga via foto? Upload di sini ya Kak!")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    st.divider()
    
    st.write("📞 WA: 0857-2226-8247")
    st.write("IG: @laundry.kamu")
    
    if st.button("🔄 Reset Chat"):
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

# --- INPUT USER (CLEAN STYLE) ---
# Input chat tetap di bawah, bersih tanpa gangguan tombol lain
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
    
    # Simpan history (Cek agar tidak double input saat upload)
    # Trik: Kita hanya simpan history jika ini adalah interaksi baru
    current_content = prompt if prompt else f"[Mengirim file: {uploaded_file.name}]"
    
    # Cek pesan terakhir agar tidak duplikat di history visual
    if len(st.session_state.messages) > 0:
        if st.session_state.messages[-1]["content"] != current_content:
            st.session_state.messages.append({"role": "user", "content": current_content})
    else:
        st.session_state.messages.append({"role": "user", "content": current_content})

    # 2. Siapkan Data
    parts_to_send = [SOP_ADMIN]
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            parts_to_send.append(img_data)
        except:
            pass
    
    if prompt: parts_to_send.append(prompt)
    else: parts_to_send.append("Analisis gambar/file ini.")

    # 3. Kirim ke AI (Anti-Error System)
    bot_reply = ""
    # Cek apakah pesan terakhir adalah dari asisten? Jika ya, jangan jawab lagi (mencegah loop)
    if st.session_state.messages[-1]["role"] != "assistant":
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
