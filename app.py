import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse # Alat untuk membuat link WA canggih

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin Sari - Berkilau Clean", page_icon="✨", layout="wide")

# --- CSS TAMPILAN (BERSIH & RAPI) ---
st.markdown("""
<style>
    /* Kotak Chat Rapi */
    .stChatInput textarea {
        border-radius: 25px !important;
        padding: 10px 20px !important;
        border: 1px solid #ddd !important;
    }
    /* Tombol Kirim */
    .stChatInput button {
        border-radius: 50% !important;
    }
    /* Link WA Button */
    .stLinkButton a {
        background-color: #25D366 !important; /* Warna Hijau WA */
        color: white !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        text-align: center !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (UPLOAD GAMBAR & KONTAK) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=80) 
    st.title("Berkilau Clean")
    st.write("Jasa Cuci Sofa, Kasur & Karpet.")
    
    st.divider()

    # 1. TEMPAT UPLOAD DI SAMPING (SESUAI REQUEST)
    st.subheader("📸 Cek Noda/Barang")
    st.info("Upload foto di sini, nanti Sari cek harganya!")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    st.divider()
    
    # 2. KONTAK DI SAMPING
    st.subheader("📞 Kontak Agen")
    st.write("WA: **0857-2226-8247**")
    st.write("IG: **@laundry.kamu**")
    
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = [] 
        st.rerun() 

# --- UTAMA ---
st.title("✨ Chat dengan Admin Sari")
st.write("Tanya harga dulu aja Kak, kalau cocok baru booking! 😊")

# --- KUNCI API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Kunci API belum dipasang!")
        st.stop()
except:
    st.stop()

# --- SOP ADMIN CANGGIH (LOGIKA TANYA DULU BARU WA) ---
SOP_ADMIN = """
PERAN: Kamu adalah Sari, Admin CS 'Berkilau Clean'.
SIKAP: Ramah, santai, solutif, panggil 'Kak', pakai emoji (😊).

TUGAS UTAMA:
1. Jawab pertanyaan harga dan layanan DULU. Jangan langsung kasih nomor WA.
2. JELASKAN detail harga sesuai data di bawah.
3. HANYA JIKA user bilang "Mau", "Setuju", "Booking", atau "Deal", BARU arahkan ke WhatsApp.

DATA HARGA:
- Cuci Sofa: 50rb/dudukan (Kain), 60rb/dudukan (Kulit). Min order 2 dudukan.
- Cuci Kasur: 200rb (Springbed/Queen/King), 150rb (Single/Latex).
- Promo: Order Senin-Rabu GRATIS Pengharum.

ATURAN PENTING (FORMAT DEAL):
Jika user sudah setuju/mau booking, kamu WAJIB mengeluarkan ringkasan dengan format persis seperti ini di akhir chat:
"[DEAL_SUMMARY]: User mau pesan [Sebutkan itemnya] dengan estimasi harga [Sebutkan totalnya]."
"""

# --- MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo Kak! Mau cuci sofa atau kasur? Boleh kirim fotonya di menu samping ya, biar Sari cek harganya 😊"}
    ]

# TAMPILKAN HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT CHAT ---
prompt = st.chat_input("Tanya harga atau jenis layanan...")

# --- PROSES AI ---
if prompt or uploaded_file:
    # 1. TAMPILKAN PESAN USER
    with st.chat_message("user"):
        if prompt: st.write(prompt)
        if uploaded_file:
            try:
                img = Image.open(uploaded_file)
                st.image(img, width=200, caption="Foto dikirim")
            except: st.write("Mengirim foto...")
            
    # Simpan history
    txt_content = prompt if prompt else "[Mengirim Foto]"
    # Cek duplikat history visual
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != txt_content:
        st.session_state.messages.append({"role": "user", "content": txt_content})

    # 2. SIAPKAN DATA KE AI
    parts = [SOP_ADMIN]
    if uploaded_file:
        try: parts.append(Image.open(uploaded_file))
        except: pass
    if prompt: parts.append(prompt)
    else: parts.append("Tolong cek foto ini dan berikan estimasi harga.")

    # 3. AI MENJAWAB
    bot_reply = ""
    with st.chat_message("assistant"):
        with st.spinner("Sari sedang mengetik..."):
            try:
                # Ban Serep System
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(parts)
                    bot_reply = response.text
                except:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(parts)
                    bot_reply = response.text
                
                # Bersihkan tag rahasia dari tampilan chat (biar user gak lihat kode aneh)
                tampilan_user = bot_reply.replace("[DEAL_SUMMARY]:", "").strip()
                st.write(tampilan_user)
                
                st.session_state.messages.append({"role": "assistant", "content": tampilan_user})

                # --- FITUR SMART HANDOVER KE WHATSAPP ---
                # Cek apakah AI mendeteksi "DEAL" atau ada tanda ringkasan
                if "[DEAL_SUMMARY]:" in bot_reply:
                    # Ambil ringkasan pesanan yang dibuat AI
                    ringkasan = bot_reply.split("[DEAL_SUMMARY]:")[1].strip()
                    
                    st.success("✅ Wah, pilihan bagus Kak! Silakan lanjut ke WA Agen kami di bawah ini:")
                    
                    # SIAPKAN LINK WA DENGAN RIWAYAT CHAT
                    no_wa = "6285722268247"
                    
                    # Pesan otomatis yang akan muncul di WA Agen
                    pesan_awal = f"Halo Admin Berkilau Clean! 👋\nSaya mau booking dari Chatbot.\n\n*Detail Pesanan:*\n{ringkasan}\n\nMohon info jadwal kosong ya!"
                    
                    # Encode pesan agar bisa jadi Link URL
                    pesan_encoded = urllib.parse.quote(pesan_awal)
                    link_wa = f"https://wa.me/{no_wa}?text={pesan_encoded}"
                    
                    st.link_button("📲 Lanjut Booking di WhatsApp (Kirim Data)", link_wa)
                
            except Exception as e:
                st.error("Maaf Kak, sinyal lagi putus-putus. Coba tanya lagi ya 🙏")
