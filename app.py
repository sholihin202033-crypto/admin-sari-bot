import streamlit as st
import google.generativeai as genai
from PIL import Image # Tambahan library untuk proses gambar

# --- JUDUL WEBSITE ---
st.set_page_config(page_title="Admin Sari Vision", page_icon="✨")
st.title("✨ Admin Sari - Berkilau Clean")
st.write("Silakan tanya harga, atau kirim foto sofa/kasur kotor untuk dicek!")

# --- KONFIGURASI KUNCI (Auto-Detect) ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Kunci API belum dipasang di Secrets!")
        st.stop()
except Exception as e:
    st.warning("Menunggu kunci API...")
    st.stop()

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
       {"role": "assistant", "content": "Hai Kak! Saya Sari. Ada yang bisa saya bantu? Kalau ada foto sofa yang kotor, boleh dikirim ya biar saya cek 😊"} 
    ]

# --- TAMPILKAN CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- KOLOM UPLOAD GAMBAR (BARU) ---
# Menggunakan expander agar tampilan tetap rapi
with st.expander("📸 Klik di sini untuk Upload Foto (Sofa/Kasur/Noda)", expanded=False):
    uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"])
    
# --- INPUT USER ---
if prompt := st.chat_input("Ketik pesanmu di sini..."):
    
    # 1. Tampilkan & Simpan Pesan User
    with st.chat_message("user"):
        st.write(prompt)
        image_data = None
        if uploaded_file:
            # Jika ada gambar, tampilkan di chat dan siapkan untuk AI
            image_data = Image.open(uploaded_file)
            st.image(image_data, caption="Foto dikirim", width=300)
    
    # Simpan history (Text saja agar hemat memori)
    st.session_state.messages.append({"role": "user", "content": prompt})
    if uploaded_file:
        st.session_state.messages.append({"role": "user", "content": "[User mengirimkan gambar]"})

    # 2. Siapkan Data/SOP (Diupdate untuk instruksi Gambar)
    SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean' (Nama: Sari).
Sikap: Ramah, santai, solutif, selalu menggunakan kata 'Kak' dan emoji yang sopan (😊, 👍, 🙏).

INSTRUKSI ANALISIS GAMBAR:
- Jika user mengirim gambar, perhatikan kondisinya (noda, jenis bahan, atau tingkat kekotoran).
- Berikan komentar empati seperti "Waduh, nodanya lumayan terlihat ya Kak" atau "Wah, ini bahan beludru ya Kak, butuh penanganan khusus."
- Hubungkan kondisi gambar dengan layanan yang sesuai.

DATA LENGKAP PRODUK DAN HARGA:
1. CUCI SOFA:
   - Sofa Standar (Kain): Rp 50.000 / dudukan.
   - Sofa Bahan Khusus (Kulit/Beludru): Rp 60.000 / dudukan.
   - Min. Order: 2 dudukan.
2. CUCI KASUR:
   - Springbed (Semua Ukuran): Rp 200.000.
   - Kasur Busa/Latex: Rp 150.000.
3. PROMO AKTIF:
   - Booking Senin-Rabu GRATIS 1 Pengharum Ruangan.

ATURAN CHAT:
- Akhiri dengan Call-to-Action: "Apakah Kakak mau langsung dijadwalkan?"
- Minta data alamat & WA jika deal.
"""

    # 3. Kirim ke AI
    try:
        # A. Siapkan History Chat (Text Only dari masa lalu)
        history_parts = [{"role": "user", "parts": [SOP_ADMIN]}]
        
        # Ambil pesan-pesan sebelumnya (kecuali yang barusan dikirim) untuk konteks
        # Kita filter agar hanya teks yang masuk ke history loop sederhana ini
        for m in st.session_state.messages[:-2 if uploaded_file else -1]:
            role = "user" if m["role"] == "user" else "model"
            history_parts.append({"role": role, "parts": [m["content"]]})

        # B. Siapkan Pesan SAAT INI (Text + Gambar)
        current_parts = [prompt]
        if image_data:
            current_parts.append(image_data) # Masukkan data gambar ke prompt
        
        history_parts.append({"role": "user", "parts": current_parts})

        # Gunakan model 'gemini-1.5-flash' yang mendukung gambar (Vision)
        # Note: 'gemini-2.5' belum rilis publik, jadi diganti ke 1.5 yg stabil
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        with st.spinner('Sari sedang melihat pesan & fotomu...'):
            response = model.generate_content(history_parts)
        
        # 4. Tampilkan Balasan
        bot_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
            
    except Exception as e:
        st.error(f"Error koneksi: {e}")
