import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse 

st.set_page_config(page_title="Admin Sari", page_icon="✨", layout="wide")

# --- CSS (Supaya Rapi) ---
st.markdown("""
<style>
    /* Chat Bubble */
    [data-testid="stChatMessage"]:nth-child(odd) { background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 15px; }
    [data-testid="stChatMessage"]:nth-child(even) { background-color: #fff; border: 1px solid #f0f0f0; border-radius: 15px; }
    
    /* Tombol Pilihan */
    .stButton button { width: 100%; border-radius: 20px !important; border: 1px solid #ddd !important; }
    
    /* Sidebar Upload */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] { padding: 10px; background: white; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI RESET (Perbaikan: Reset kembali ke Sapaan Awal) ---
def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! 👋 Ada yang bisa Sari bantu? (Upload foto di menu kiri ya)"}]

# --- SIDEBAR ---
with st.sidebar:
    st.title("✨ Berkilau Clean")
    st.subheader("📸 Kirim Foto")
    uploaded_file = st.file_uploader("Upload foto noda:", type=["jpg", "png"], label_visibility="collapsed")
    
    if uploaded_file:
        st.success("✅ Foto Masuk!")
        st.image(Image.open(uploaded_file), caption="Preview", use_container_width=True)
    
    st.divider()
    # Tombol Reset dengan Callback (Supaya tombol cepat muncul lagi)
    st.button("🗑️ Reset Chat", on_click=reset_chat, use_container_width=True)

# --- SETUP ---
if "messages" not in st.session_state:
    reset_chat() # Inisialisasi awal

# --- AREA CHAT UTAMA ---
st.header("💬 Chat Admin")

# === PERBAIKAN: LOGIKA TOMBOL ===
# Tombol muncul jika chat <= 1 (Artinya cuma ada sapaan awal atau kosong)
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

# --- TAMPILKAN CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT & AI ---
# (Pastikan API Key sudah ada di secrets)
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except: pass

prompt = st.chat_input("Ketik pesan...")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # ... (Bagian AI sama seperti sebelumnya) ...
    # Agar ringkas, saya buat dummy reply sederhana untuk tes tombol
    with st.chat_message("assistant"):
        with st.spinner("Mengetik..."):
            # Masukkan logika AI lengkap di sini
            reply = "Halo! Ini respon otomatis. (Fitur AI berjalan)" 
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
