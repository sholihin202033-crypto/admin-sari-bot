import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse 

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS VISUAL ---
st.markdown("""
<style>
    /* 1. KOTAK CHAT (INPUT) */
    .stChatInput textarea {
        border-radius: 25px !important;
        padding-top: 12px !important;
        border: 1px solid #ddd !important;
    }
    
    /* 2. GELEMBUNG CHAT */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e8f5e9; 
        border-radius: 15px;
        border: 1px solid #c8e6c9;
    }
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        border-radius: 15px;
        border: 1px solid #f0f0f0;
    }

    /* 3. SIDEBAR */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        padding: 10px;
        background: white;
        border: 1px dashed #ccc;
        border-radius: 10px;
    }
    
    /* 4. TOMBOL QUICK REPLY */
    .stButton button {
        border-radius: 20px !important;
        border: 1px solid #eee !important;
        background-color: white !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (UPLOAD FOTO DISINI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=60)
    st.title("Berkilau Clean")
    
    # BAGIAN 1: UPLOAD FOTO
    st.divider()
    st.subheader("📸 Kirim Foto")
    st.caption("Upload foto noda/sofa di sini:")
    
    uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file:
        st.success("✅ Foto Terkirim!")
        img = Image.open(uploaded_file)
        st.image(img, caption="Preview Foto", use_container_width=True)
    else:
        st.info("Belum ada foto.")
        
    st.divider()
    
    # BAGIAN 2: INFO LAIN
    with st.expander("📋 Daftar Harga"):
        st.markdown("""
        **Sofa:** 50rb/dudukan
        **Kasur:** 150rb-200rb
        **Karpet:** 15rb/m
        """)
    
    st.write("📞 WA: 0857-2226-8247")
    
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- HEADER & API ---
st.image("https://img.freepik.com/free-vector/cleaning-service-banner-template_23-2148536647.jpg?w=1380", use_container_width=True)

try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.warning("⚠️ Masukkan API Key dulu ya.")
        st.stop()
except:
    st.stop()

SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean'.
SIKAP: Ramah, santai, solutif, panggil 'Kak'.
TUGAS:
1. Jawab pertanyaan harga/layanan.
2. Cek gambar jika user upload foto di sidebar.
3. HANYA jika user bilang "Deal/Booking", buat ringkasan rahasia: "[DEAL_SUMMARY]: ...".
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo Kak! 👋 Ada yang bisa Sari bantu? Kalau mau cek noda, upload fotonya di menu sebelah kiri ya."}]

# --- AREA CHAT UTAMA ---
st.subheader("💬 Chat")

# === INI TOMBOL YANG TADI HILANG (SUDAH DIKEMBALIKAN) ===
if len(st.session_state.messages) == 1:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛋️ Cuci Sofa", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Berapa harga cuci sofa?"})
            st.rerun()
    with col2:
        if st.button("🛏️ Cuci Kasur", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Berapa harga cuci kasur?"})
            st.rerun()
    with col3:
        if st.button("📍 Lokasi", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Melayani area mana saja?"})
            st.rerun()
# ========================================================

# TAMPILKAN HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT CHAT ---
prompt = st.chat_input("Ketik pesan...")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
        if uploaded_file:
            st.caption("*(Melampirkan foto dari sidebar)*")
    st.session_state.messages.append({"role": "user", "content": prompt})

    parts = [SOP_ADMIN]
    
    if uploaded_file:
        try:
            img_ai = Image.open(uploaded_file)
            parts.append(img_ai)
            parts.append(f"User bertanya: '{prompt}'. Jawab berdasarkan gambar yang ada di sidebar.")
        except:
            parts.append(prompt)
    else:
        parts.append(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Mengetik..."):
            try:
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                except:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(parts)
                
                bot_reply = response.text
                tampilan_user = bot_reply.replace("[DEAL_SUMMARY]:", "").strip()
                st.write(tampilan_user)
                st.session_state.messages.append({"role": "assistant", "content": tampilan_user})
                
                if "[DEAL_SUMMARY]:" in bot_reply:
                    ringkasan = bot_reply.split("[DEAL_SUMMARY]:")[1].strip()
                    st.success("✅ Oke Kak, lanjut ke WA ya:")
                    no_wa = "6285722268247"
                    pesan = urllib.parse.quote(f"Halo Admin! Mau booking.\n\nInfo:\n{ringkasan}")
                    link_wa = f"https://wa.me/{no_wa}?text={pesan}"
                    st.link_button("📲 BUKA WHATSAPP", link_wa, use_container_width=True)

            except Exception as e:
                st.error("Maaf, ada gangguan jaringan.")
