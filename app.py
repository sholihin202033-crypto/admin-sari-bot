import streamlit as st
import google.generativeai as genai

st.title("🔍 Cek Ketersediaan Model")

try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        st.success("API Key ditemukan!")
    else:
        st.error("API Key tidak ada di Secrets.")
        st.stop()
        
    st.write("Sedang menghubungi Google untuk minta daftar model...")
    
    # KITA MINTA DAFTAR MODEL YANG TERSEDIA
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            st.write(f"- {m.name}")
            
    st.write("---")
    if "models/gemini-1.5-flash" in available_models:
        st.success("✅ HORE! gemini-1.5-flash TERSEDIA! Masalahmu ada di 'Reboot' saja.")
    else:
        st.warning("⚠️ Model 1.5-flash TIDAK MUNCUL. Gunakan salah satu nama model di atas.")

except Exception as e:
    st.error(f"Error parah: {e}")
    st.info("Tips: Pastikan file requirements.txt isinya: google-generativeai>=0.7.2")
