import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse 

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari", page_icon="✨", layout="wide")

# --- CSS AGAR TAMPILAN RAPI DI HP ---
st.markdown("""
<style>
    /* Gelembung Chat */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e8f5e9; 
        border: 1px solid #c8e6c9;
        border-radius: 15px; 
    }
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        border: 1px solid #f0f0f0; 
        border-radius: 15px;
    }
    
    /* Tombol Pilihan (Supaya full width di HP) */
    .stButton button {
        width: 100%;
        border-radius: 20px !important;
        border: 1px solid #ddd !important;
        background-color: white !important;
    }
    .stButton button:hover {
        border-color: #4CAF50 !important;
        color: #4CAF50 !important;
    }
    
    /* Kotak Upload di Sidebar */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        padding: 10px;
        background: white;
        border-radius: 10px;
        border: 1px dashed #aaa;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI RESET (Supaya chat bersih) ---
def reset_chat():
    # Sapaan baru untuk menandakan kode baru sudah aktif
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! 👋 Admin Sari siap bantu cek harga & noda. Silakan pilih menu di bawah atau ketik manual ya 👇"}]

# --- SIDEBAR (PANEL KIRI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=60)
    st.title("Berkilau Clean")
    
    # 1. Upload Foto
    st.subheader("📸 Kirim Foto Noda")
    st.caption("Upload foto di sini agar Sari bisa lihat:")
    uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        st.success("✅ Foto Diterima!")
        st.image(Image.open(uploaded_file), caption="Preview Foto", use_container_width=True)
    
    st.divider()
    
    # 2. Tombol Reset
    # Gunakan on_click agar halaman refresh otomatis
    st.button("🗑️ Mulai Chat Baru", on_click=reset_chat, use_container_width=True)
    
    st.info("📞 WA: 0857-2226-8247")

# --- INISIALISASI SESSION STATE ---
if "messages" not in st.session_state:
    reset_chat()

# --- HEADER GAMBAR ---
st.image("https://img.freepik.com/free-vector/cleaning-service-banner-template_23-2148536647.jpg?w=1380", use_container_width=True)

# --- AREA CHAT UTAMA ---
st.subheader("💬 Chat Admin")

# === TOMBOL CEPAT (AKAN MUNCUL JIKA CHAT BARU DIMULAI) ===
# Logika: Muncul jika jumlah pesan <= 1 (cuma sapaan)
if len(st.session_state.messages) <= 1:
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

# --- TAMPILKAN RIWAYAT CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT CHAT ---
prompt = st.chat_input("Ketik pesan...")

# --- PROSES UTAMA ---
if prompt:
    # 1. Tampilkan Chat User
    with st.chat_message("user"):
        st.write(prompt)
        if uploaded_file:
            st.caption("*(Melampirkan foto dari sidebar)*")
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Setup AI
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # SOP ADMIN
        SOP_ADMIN = """
        PERAN: Sari (Admin Berkilau Clean).
        DATA HARGA: Sofa (50rb/dudukan), Kasur (150-200rb), Karpet (15rb/m).
        TUGAS: Jawab ramah. Jika user kirim gambar, komentari nodanya.
        KEYWORD DEAL: Jika user fix mau booking, akhiri dengan format:
        "[DEAL_SUMMARY]: User mau [Jasa], Estimasi [Harga]."
        """
        
        parts = [SOP_ADMIN]
        if uploaded_file:
            try:
                parts.append(Image.open(uploaded_file))
                parts.append(f"User bertanya: {prompt}. Jawab berdasarkan foto yang diupload.")
            except: parts.append(prompt)
        else:
            parts.append(prompt)

        # 3. Respon AI
        with st.chat_message("assistant"):
            with st.spinner("Sari sedang mengetik..."):
                # Pilih Model (Fallback System)
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                except:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(parts)
                
                bot_reply = response.text
                
                # Bersihkan kode rahasia dari chat bubble
                tampilan_user = bot_reply.replace("[DEAL_SUMMARY]:", "").strip()
                st.write(tampilan_user)
                st.session_state.messages.append({"role": "assistant", "content": tampilan_user})
                
                # Cek Trigger WA
                if "[DEAL_SUMMARY]:" in bot_reply:
                    summary = bot_reply.split("[DEAL_SUMMARY]:")[1].strip()
                    st.success("✅ Oke Kak! Lanjut ke WA ya untuk atur jadwal:")
                    
                    wa_url = f"https://wa.me/6285722268247?text={urllib.parse.quote(f'Halo Admin! Saya mau booking.\n\n{summary}')}"
                    st.link_button("📲 BUKA WHATSAPP SEKARANG", wa_url, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}. Pastikan API Key benar.")
