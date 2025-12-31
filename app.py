import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS "JURUS RAHASIA" (UNTUK MENYATUKAN TOMBOL & CHAT) ---
st.markdown("""
<style>
    /* 1. MEMBUAT TOMBOL (+) MELAYANG DI POJOK KIRI BAWAH */
    [data-testid="stPopover"] {
        position: fixed;
        bottom: 25px; /* Jarak dari bawah layar */
        left: 15px;   /* Jarak dari kiri layar */
        z-index: 1000; /* Agar tombol selalu di paling depan */
    }

    /* 2. MENGUBAH BENTUK TOMBOL (+) JADI BULAT */
    [data-testid="stPopover"] > div > button {
        border-radius: 50%;
        width: 45px;
        height: 45px;
        background-color: #f0f2f6;
        border: 2px solid #ddd;
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); /* Efek bayangan */
    }

    /* 3. MENGGESER KOLOM KETIK SUPAYA TIDAK KETABRAK TOMBOL (+) */
    .stChatInput textarea {
        padding-left: 60px !important; /* Memberi ruang kosong di kiri untuk tombol + */
        border-radius: 30px !important; /* Membuat kotak chat lonjong */
        border: 1px solid #ccc !important;
    }
    
    /* 4. MENGHILANGKAN GARIS FOKUS YANG MENGGANGGU */
    .stChatInput textarea:focus {
        box-shadow: none !important;
        border-color: #777 !important;
    }
    
    /* 5. MERAPIKAN TAMPILAN PESAN */
    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU SAMPING) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=80) 
    st.title("Berkilau Clean")
    st.write("Jasa kebersihan profesional.")
    
    st.divider()
    
    st.subheader("📞 Kontak Kami")
    st.write("WA: **0857-2226-8247**")
    st.write("IG: **@laundry.kamu**") # <-- SUDAH DITAMBAHKAN
    
    st.divider()
    
    if st.button("🔄 Hapus Chat"):
        st.session_state.messages = [] 
        st.rerun() 

# --- HEADER UTAMA ---
st.title("✨ Admin Sari")
st.caption("Online 24 Jam • Balas Cepat • Solutif")

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
        {"role": "assistant", "content": "Halo Kak! Sari di sini. Ada yang bisa dibantu? Boleh kirim foto noda di sofa/kasurnya ya 😊"}
    ]

# TAMPILKAN CHAT (SEJARAH)
# Kita tambahkan wadah kosong di bawah agar chat terakhir tidak tertutup tombol
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
st.write("") # Spasi kosong tambahan di bawah
st.write("") 

# --- AREA INPUT (TOMBOL + DAN CHAT MENYATU) ---

# 1. TOMBOL UPLOAD (+)
# Berkat CSS di atas, tombol ini akan 'terbang' ke pojok kiri bawah layar
with st.popover("➕"):
    st.write("Lampirkan File:")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

# 2. KOLOM CHAT (INPUT)
# Ini otomatis ada di paling bawah (Sticky Bottom)
prompt = st.chat_input("Ketik pesan...")

# --- PROSES CHAT ---
if prompt or uploaded_file:
    # A. TAMPILKAN PESAN USER
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file: 
            try:
                img = Image.open(uploaded_file)
                st.image(img, caption="Foto dikirim", width=250)
            except:
                st.write(f"📄 Mengirim file")
    
    # Simpan ke memori (Hanya jika beda dengan terakhir untuk mencegah duplikat visual)
    msg_content = prompt if prompt else "[Mengirim foto]"
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != msg_content:
        st.session_state.messages.append({"role": "user", "content": msg_content})

    # B. SIAPKAN DATA KE AI
    parts_to_send = [SOP_ADMIN]
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            parts_to_send.append(img_data)
        except: pass
    
    if prompt: parts_to_send.append(prompt)
    else: parts_to_send.append("Analisis gambar ini.")

    # C. AI MENJAWAB (ANTI-ERROR)
    # Cek agar AI tidak menjawab dirinya sendiri
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Sari sedang mengetik..."):
                try:
                    # Coba Mesin 1
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts_to_send)
                    bot_reply = response.text
                except:
                    try:
                        # Coba Mesin 2 (Cadangan)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(parts_to_send)
                        bot_reply = response.text
                    except:
                        bot_reply = "Maaf Kak, sinyal Sari lagi gangguan. Coba tanya lagi ya 🙏"

                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})

                # LINK WHATSAPP OTOMATIS
                if any(x in bot_reply.lower() for x in ["jadwal", "whatsapp", "wa", "booking"]):
                    st.info("👇 Lanjut ke WhatsApp Admin:")
                    no_wa = "6285722268247"
                    pesan_wa = "Halo Admin Berkilau Clean, mau pesan jasa cuci (dari Chatbot)."
                    link = f"https://wa.me/{no_wa}?text={pesan_wa.replace(' ', '%20')}"
                    st.link_button("📲 Chat WhatsApp", link)
