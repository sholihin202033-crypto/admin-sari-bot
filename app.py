import streamlit as st
import google.generativeai as genai

# --- JUDUL WEBSITE ---
st.set_page_config(page_title="Admin Sari", page_icon="✨")
st.title("✨ Admin Sari - Berkilau Clean")
st.write("Silakan tanya harga atau layanan kami di bawah ini!")

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
       {"role": "assistant", "content": "Hai Kak! Saya Sari. Mau cuci sofa atau kasur? 😊"} 
    ]
# --- TAMPILKAN CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT USER ---
if prompt := st.chat_input("Ketik pesanmu di sini..."):
    # 1. Simpan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Siapkan Data/SOP
    SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean' (Nama: Sari).
Sikap: Ramah, santai, solutif, selalu menggunakan kata 'Kak' dan emoji yang sopan (😊, 👍, 🙏).

DATA LENGKAP PRODUK DAN HARGA:
1. CUCI SOFA:
   - Sofa Standar (Kain): Rp 50.000 / dudukan.
   - Sofa Bahan Khusus (Kulit/Beludru): Rp 60.000 / dudukan.
   - Min. Order: 2 dudukan.
2. CUCI KASUR:
   - Springbed (Semua Ukuran): Rp 200.000.
   - Kasur Busa/Latex: Rp 150.000.
   - Keunggulan: Bebas Tungau, Kering 90% dalam 3 jam.
3. DEEP CLEANING (PEMBERSIHAN TOTAL):
   - Untuk Rumah Baru/Pindahan: Rp 50.000 / m2.
   - Min. Order: 20 m2.
4. PROMO AKTIF:
   - Setiap booking di hari Senin-Rabu, dapat GRATIS 1 Pengharum Ruangan Premium.

ATURAN CHAT:
- Setelah memberikan informasi harga, selalu akhiri dengan pertanyaan Call-to-Action seperti: "Apakah Kakak mau langsung dijadwalkan?"
- Jika pelanggan setuju/deal, minta data ini: "Mohon kirimkan data lengkap: (1) Alamat Lengkap, (2) Nama Kontak, (3) Nomor WA aktif. Agar tim kami bisa segera berangkat ya, Kak."
- Jangan menjawab pertanyaan di luar layanan kebersihan.
"""

    # 3. Kirim ke AI
    try:
        # Gabungkan SOP + Chat History
        full_chat = [{"role": "user", "parts": [SOP_ADMIN]}]
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            full_chat.append({"role": role, "parts": [m["content"]]})

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(full_chat)
        
        # 4. Tampilkan Balasan
        bot_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
            
    except Exception as e:
        st.error(f"Error koneksi: {e}")
