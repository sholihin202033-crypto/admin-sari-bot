import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari", page_icon="✨", layout="wide")

# --- CSS KHUSUS (AGAR TOMBOL MASUK KE DALAM KOTAK CHAT) ---
st.markdown("""
<style>
    /* 1. MENGATUR KOTAK KETIK (INPUT) */
    .stChatInput textarea {
        border-radius: 25px !important; /* Membuat sudut bulat */
        padding-left: 50px !important;  /* MEMBUAT RUANG KOSONG DI KIRI DALAM */
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        border: 1px solid #ccc !important; /* Garis pinggir abu halus */
    }

    /* 2. MENGATUR POSISI TOMBOL (+) AGAR MASUK KE DALAM RUANG KOSONG TADI */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 28px !important; /* Atur ketinggian agar pas di tengah kotak input */
        left: 18px !important;   /* Geser agar masuk ke sisi kiri kotak input */
        z-index: 99999 !important; /* Pastikan tombol ada di lapisan paling atas */
        width: 40px !important;
        height: 40px !important;
    }

    /* 3. MENGUBAH TAMPILAN TOMBOL (+) MENJADI IKON TRANSPARAN */
    [data-testid="stPopover"] > div > button {
        background-color: transparent !important; /* Latar bening biar menyatu */
        border: none !important;       /* Hilangkan kotak tombol */
        color: #555 !important;        /* Warna ikon abu gelap */
        font-size: 28px !important;    /* Ukuran ikon */
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: none !important;
    }
    
    /* Efek saat tombol ditekan */
    [data-testid="stPopover"] > div > button:hover {
        color: #000 !important;
        background-color: rgba(0,0,0,0.05) !important;
        border-radius: 50% !important;
    }
    
    /* Efek saat tombol aktif (diklik) */
    [data-testid="stPopover"] > div > button:active {
        background-color: rgba(0,0,0,0.1) !important;
    }

    /* 4. MENGHILANGKAN EFEK GARIS BIRU SAAT MENGETIK */
    .stChatInput textarea:focus {
        box-shadow: none !important;
        border-color: #888 !important;
    }
    
    /* 5. MENYEMBUNYIKAN HEADER BAWAAN POP-OVER BIAR BERSIH */
    div[data-testid="stPopoverBody"] {
        border-radius: 15px !important;
    }

</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=80) 
    st.title("Berkilau Clean")
    st.divider()
    st.write("📞 WA: 0857-2226-8247")
    st.write("IG: @laundry.kamu")
    if st.button("🗑️ Hapus Chat"):
        st.session_state.messages = []
        st.rerun()

# --- UTAMA ---
st.title("Admin Sari ✨")
st.write("Jasa Cuci Sofa, Kasur & Karpet (24 Jam)")

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
PERAN: Kamu Admin Sari (Berkilau Clean).
SIKAP: Ramah, santai, pakai emoji 😊.
HARGA:
- Sofa: 50rb/dudukan.
- Kasur Springbed: 200rb.
TUJUAN: Jawab harga & arahkan ke WhatsApp.
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! Mau cuci apa? Boleh kirim foto nodanya ya 😊"}]

# TAMPILKAN HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
st.write("") 
st.write("") # Spasi bawah biar chat tidak ketutup

# --- BAGIAN PENTING: TOMBOL MENYATU DENGAN CHAT ---

# 1. TOMBOL UPLOAD (+)
# Berkat CSS di atas, tombol ini akan dipaksa masuk ke dalam kotak chat sebelah kiri
with st.popover("➕"):
    st.caption("Pilih Gambar:")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

# 2. KOLOM CHAT
prompt = st.chat_input("Ketik pesan...")

# --- LOGIKA ---
if prompt or uploaded_file:
    # INPUT USER
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file:
            try:
                img = Image.open(uploaded_file)
                st.image(img, width=200)
            except:
                st.write(f"📁 {uploaded_file.name}")

    # HISTORY
    txt = prompt if prompt else "[Kirim File]"
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != txt:
        st.session_state.messages.append({"role": "user", "content": txt})

    # PROSES AI
    parts = [SOP_ADMIN]
    if uploaded_file:
        try: parts.append(Image.open(uploaded_file))
        except: pass
    if prompt: parts.append(prompt)
    else: parts.append("Analisis gambar ini.")

    # JAWABAN AI
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("..."):
                try:
                    # Coba Mesin Terbaru
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                    reply = response.text
                except:
                    try:
                        # Coba Mesin Stabil
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(parts)
                        reply = response.text
                    except:
                        reply = "Maaf Kak, error jaringan. Coba lagi ya 🙏"
                
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                # TOMBOL WA
                if "wa" in reply.lower() or "booking" in reply.lower():
                    link = "https://wa.me/6285722268247?text=Halo%20Admin%20Berkilau"
                    st.link_button("📲 Chat WhatsApp", link)
