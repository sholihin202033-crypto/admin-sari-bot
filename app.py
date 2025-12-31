import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse 

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS VISUAL (Disederhanakan) ---
st.markdown("""
<style>
    /* 1. KOTAK CHAT (INPUT) - GAYA KAPSUL */
    .stChatInput textarea {
        border-radius: 25px !important;
        padding-top: 12px !important;
        border: 1px solid #ddd !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05) !important;
    }
    
    /* 2. GELEMBUNG CHAT (CHAT BUBBLES) */
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

    /* 3. TOMBOL QUICK REPLY */
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
    
    /* 4. UPLOAD FILE DI SIDEBAR */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        padding: 10px;
        border: 1px dashed #ccc;
        border-radius: 10px;
        text-align: center;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] .stImage {
        margin-top: 10px;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU KIRI & PANEL FOTO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=60)
    st.title("Berkilau Clean")
    st.info("Jasa Cuci Sofa, Kasur & Karpet")
    st.divider()
    
    # Menu Harga
    with st.expander("📋 Intip Daftar Harga"):
        st.markdown("""
        **Sofa:** 50rb - 60rb / dudukan
        **Kasur:** 150rb - 200rb / unit
        **Karpet:** 15rb / meter
        """)
    
    st.divider()
    
    # --- PANEL FOTO (DIPINDAHKAN KESINI) ---
    st.subheader("🖼️ Panel Foto")
    st.caption("Upload foto noda/sofa disini untuk dicek Sari:")
    
    # File Uploader
    uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    # Preview Gambar di Sidebar
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Foto Terupload", use_container_width=True)
        st.success("✅ Foto siap dikirim")
    else:
        st.info("Belum ada foto.")
    
    st.divider()
    
    # Kontak & Tombol Hapus
    st.write("📞 WA: 0857-2226-8247")
    if st.button("🗑️ Hapus Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- HEADER & API KEY (TIDAK BERUBAH) ---
st.image("https://img.freepik.com/free-vector/cleaning-service-banner-template_23-2148536647.jpg?w=1380", use_container_width=True)

try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.warning("⚠️ Masukkan API Key di secrets.toml")
        st.stop()
except:
    st.stop()

SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean'.
SIKAP: Ramah, santai, solutif, panggil 'Kak', pakai emoji (😊).
TUGAS UTAMA:
1. Jawab pertanyaan harga dan layanan DULU. Analisis gambar jika ada.
2. HANYA JIKA user bilang "Mau", "Setuju", "Booking", atau "Deal", BARU arahkan ke WhatsApp.
DATA HARGA:
- Cuci Sofa: 50rb/dudukan (Kain), 60rb/dudukan (Kulit). Min 2 dudukan.
- Cuci Kasur: 200rb (Springbed), 150rb (Latex/Busa).
ATURAN DEAL:
Jika user deal/mau booking, akhiri pesanmu dengan:
"[DEAL_SUMMARY]: User mau pesan [Item] estimasi [Harga]."
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! Mau cuci apa hari ini? Kalau ada fotonya, boleh upload di panel samping ya 👉😊"}]

# --- AREA CHAT UTAMA ---
st.subheader("💬 Chat dengan Sari")

# TOMBOL CEPAT
if len(st.session_state.messages) == 1:
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

# --- INPUT CHAT & PROSES AI ---
prompt = st.chat_input("Ketik pesan untuk Sari...")

if prompt:
    # 1. Tampilkan Chat User
    with st.chat_message("user"):
        st.write(prompt)
        # Tambahkan indikator jika user mengirim pesan saat ada file di panel samping
        if uploaded_file:
            st.caption("*(Mengirim pesan dengan lampiran foto dari sidebar)*")
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Siapkan Data untuk AI
    parts = [SOP_ADMIN]
    
    # Cek apakah ada gambar di SIDEBAR yang sedang aktif
    if uploaded_file:
        try:
            # Gunakan file dari sidebar
            img_for_ai = Image.open(uploaded_file)
            parts.append(img_for_ai)
            # Tambahkan konteks eksplisit
            parts.append(f"User bertanya: '{prompt}'. Tolong analisis gambar yang ada di sidebar dan jawab pertanyaannya.")
        except Exception as e:
            # Jika gagal load gambar, tetap kirim text prompt
            parts.append(prompt)
            st.error(f"Gagal memproses gambar: {e}")
    else:
        parts.append(prompt)

    # 3. Jawaban AI
    with st.chat_message("assistant"):
        with st.spinner("Sari sedang mengetik..."):
            try:
                # Model Fallback
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                except:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(parts)
                
                bot_reply = response.text
                
                # Bersihkan kode rahasia
                tampilan_user = bot_reply.replace("[DEAL_SUMMARY]:", "").strip()
                st.write(tampilan_user)
                st.session_state.messages.append({"role": "assistant", "content": tampilan_user})
                
                # LOGIKA WA
                if "[DEAL_SUMMARY]:" in bot_reply:
                    ringkasan = bot_reply.split("[DEAL_SUMMARY]:")[1].strip()
                    st.success("✅ Siap Kak! Data sudah Sari catat. Lanjut ke WA ya:")
                    
                    no_wa = "6285722268247"
                    pesan_awal = f"Halo Admin! Saya mau booking.\n\n*Ringkasan:*\n{ringkasan}\n\nMohon info jadwal!"
                    pesan_encoded = urllib.parse.quote(pesan_awal)
                    link_wa = f"https://wa.me/{no_wa}?text={pesan_encoded}"
                    
                    st.link_button("📲 LANJUT KE WHATSAPP (BOOKING)", link_wa, use_container_width=True)

            except Exception as e:
                st.error(f"Maaf Kak, ada gangguan teknis. Error: {e}")
