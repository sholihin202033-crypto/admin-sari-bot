import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari", page_icon="✨", layout="wide")

# --- CSS "MANIPULASI VISUAL" (AGAR TOMBOL MASUK KE DALAM CHAT) ---
st.markdown("""
<style>
    /* 1. KOTAK CHAT (INPUT) */
    .stChatInput textarea {
        border-radius: 30px !important; /* Membulatkan sudut */
        padding-left: 55px !important;  /* MEMBUAT LUBANG KOSONG DI KIRI */
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        border: 1px solid #ccc !important;
    }

    /* 2. MEMAKSA TOMBOL (+) MASUK KE DALAM LUBANG TADI */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 30px !important; /* Mengatur ketinggian agar pas di tengah kotak */
        left: 20px !important;   /* Mengatur jarak dari kiri */
        z-index: 99999 !important; /* Supaya tombol ada di lapisan paling atas */
    }

    /* 3. MEMPERCANTIK TOMBOL (+) */
    [data-testid="stPopover"] > div > button {
        border-radius: 50% !important; /* Bulat sempurna */
        width: 38px !important;        /* Ukuran diperkecil dikit biar muat */
        height: 38px !important;
        background-color: transparent !important; /* Transparan biar menyatu */
        border: none !important;       /* Hapus garis kotak tombol */
        color: #555 !important;        /* Warna ikon abu tua */
        font-size: 24px !important;
        padding: 0 !important;
    }
    
    /* Efek saat tombol disentuh */
    [data-testid="stPopover"] > div > button:hover {
        background-color: #f0f0f0 !important;
        color: #000 !important;
    }

    /* 4. MENGHILANGKAN GARIS FOKUS BIRU YANG JELEK */
    .stChatInput textarea:focus {
        box-shadow: none !important;
        border-color: #888 !important;
    }
    
    /* 5. MENYEMBUNYIKAN TOMBOL KIRIM BAWAAN (OPSIONAL - BIAR LEBIH BERSIH) */
    /* .stChatInput button { display: none; } */ 
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("Berkilau Clean ✨")
    st.write("Jasa Cuci Sofa & Kasur")
    st.divider()
    st.write("📞 WA: 0857-2226-8247")
    st.write("IG: @laundry.kamu")
    if st.button("🔄 Hapus Chat"):
        st.session_state.messages = []
        st.rerun()

# --- HEADER ---
st.title("Admin Sari")
st.write("Siap bantu cek harga 24 Jam!")

# --- API KEY ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.stop()
except:
    st.stop()

# --- SOP ---
SOP_ADMIN = """
PERAN: Admin Sari (Berkilau Clean).
SIKAP: Ramah, santai, pakai emoji 😊.
HARGA:
- Sofa: 50rb/dudukan.
- Kasur: 200rb (Springbed).
TUJUAN: Jawab harga & arahkan ke WhatsApp.
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! Mau cuci apa hari ini? 😊"}]

# TAMPILKAN HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
st.write("") # Jarak aman di bawah

# --- BAGIAN KRUSIAL: TOMBOL (+) DAN CHAT ---

# 1. TOMBOL POP-UP (Akan dipindah paksa oleh CSS ke dalam kotak chat)
with st.popover("➕"):
    st.caption("Upload Foto:")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

# 2. INPUT CHAT UTAMA
prompt = st.chat_input("Ketik pesan...")

# --- LOGIKA PROGRAM ---
if prompt or uploaded_file:
    # TAMPILKAN INPUT USER
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file:
            try:
                img = Image.open(uploaded_file)
                st.image(img, width=200)
            except:
                st.write(f"📁 {uploaded_file.name}")

    # SIMPAN KE HISTORY
    content_str = prompt if prompt else "[Mengirim File]"
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != content_str:
        st.session_state.messages.append({"role": "user", "content": content_str})

    # SIAPKAN DATA KE AI
    parts = [SOP_ADMIN]
    if uploaded_file:
        try: parts.append(Image.open(uploaded_file))
        except: pass
    if prompt: parts.append(prompt)
    else: parts.append("Analisis gambar ini.")

    # AI MENJAWAB
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("..."):
                try:
                    # Model Utama
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                    reply = response.text
                except:
                    try:
                        # Model Cadangan
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(parts)
                        reply = response.text
                    except:
                        reply = "Maaf Kak, error sebentar. Coba lagi ya 🙏"
                
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                if "wa" in reply.lower() or "booking" in reply.lower():
                    link = "https://wa.me/6285722268247?text=Halo%20Admin%20Berkilau"
                    st.link_button("📲 Chat WhatsApp", link)
