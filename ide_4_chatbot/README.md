# Dokumentasi Proyek: Sistem 4 - AI Chatbot Asisten Kos Putri
**Dataset:** Direktori Kos Putri SCBD  
**Teknologi:** Python, Pandas, Regular Expressions (Regex), Natural Language Pattern Matching, Streamlit Chat Components

---

## 1. Konsep & Arsitektur
Sistem ini memungkinkan pencari kos berinteraksi dengan dataset menggunakan bahasa percakapan sehari-hari (*Conversational Interface*):
1. **Entity Extraction (Ekstraksi Entitas):**
   - Mendeteksi angka anggaran belanja (*budget*) dari berbagai gaya bahasa (misal: "1.2jt", "1.5 juta", "800rb", "700000").
   - Mendeteksi fasilitas wajib (AC, Kamar Mandi Dalam, Wi-Fi, Listrik).
   - Mendeteksi nama area populer (Kledokan, Seturan, Ngropoh, Condongcatur, Puluhdadi, Dabag, UPN, YKPN).
2. **Deterministic Context Retrieval:**
   - Menyaring data kos yang memenuhi seluruh entitas yang diekstrak.
   - Mengurutkan kandidat kos dari harga termurah.
3. **Conversational Response Generator:**
   - Menghasilkan respon teks yang ramah, ringkas, dan langsung menyematkan tautan WhatsApp dan Google Maps.

---

## 2. Struktur File
```
ide_4_chatbot/
├── chatbot.ipynb    # Eksplorasi & pengujian NLP regex parser
├── app_chatbot.py   # Web UI interaktif ruang chat (st.chat_message)
└── README.md        # Dokumentasi teknis sistem 4
```

## 3. Cara Menjalankan
Jalankan aplikasi chatbot mandiri:
```bash
streamlit run ide_4_chatbot/app_chatbot.py
```
