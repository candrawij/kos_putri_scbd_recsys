# 🏘️ Portal Data Science & Sistem Pencarian Kos Putri SCBD

> Platform analitik data, direktori pencarian interaktif, sistem rekomendasi cerdas, peta sebaran spasial, dan asisten AI pencari kos putri di kawasan Seturan, Babarsari, dan sekitarnya (Sleman, D.I. Yogyakarta).

---

## 📌 Ringkasan Proyek

Proyek ini mendemonstrasikan alur lengkap pengerjaan **Data Science & Engineering end-to-end**:
1. **Data Understanding & Profiling:** Menganalisis karakteristik data mentah lapangan (*unstructured / semi-structured*).
2. **Data Cleaning & Preprocessing:** Menangani missing values, membersihkan karakter baris baru (`\n`), menormalisasi nomor WhatsApp ke standar internasional, dan menstandarisasi tautan lokasi Google Maps.
3. **Feature Engineering:** Ekstraksi rentang harga numerik (`harga_min` dan `harga_max`) serta deteksi cerdas fitur fasilitas (*Boolean Flags* untuk AC, Kamar Mandi Dalam, Wi-Fi, dan Listrik) berbasis penambangan teks lintas kolom (*multi-column text mining*).
4. **Product Development:** Membangun **4 Ide Sistem Berkelanjutan** yang dapat dijalankan secara terisolasi maupun terintegrasi dalam satu portal terpadu (*All-in-One Dashboard*).

---

## 🎯 4 Pilar Sistem yang Dikembangkan

| No | Modul Sistem | Pendekatan / Algoritma | Deskripsi |
| :---: | :--- | :--- | :--- |
| **1** | **Katalog & Filter Pencarian** | *Dynamic Multi-criteria Filtering & Sorting* | Katalog interaktif dengan filter budget slider, checkbox fasilitas, pencarian teks bebas, dan sorting harga termurah/termahal. |
| **2** | **Rekomendasi Cerdas** | *Content-Based Recommendation Engine* | Perhitungan skor kecocokan multi-kriteria ($0 - 100\%$) dengan pembobotan fleksibel antara anggaran, fasilitas prioritas, dan lokasi. |
| **3** | **Peta Sebaran Spasial** | *Geospatial Mapping (Folium & CartoDB)* | Pemetaan interaktif titik kos dengan penanda warna berbasis harga (Hijau, Kuning, Merah) serta radius kampus (UPN, STIE YKPN, Atma Jaya). |
| **4** | **Chatbot Asisten AI** | *NLP Entity Extraction & Context Retrieval* | Antarmuka obrolan percakapan yang mengekstrak anggaran, fasilitas, dan area dari pertanyaan bahasa sehari-hari. |

---

## 📁 Struktur Repositori

```
Kos putri SCBD/
│
├── data/                                    # Dataset Mentah & Bersih
│   ├── KOST PUTRI SCBD - Kost Putri.csv     # Data mentah hasil survei
│   └── kost_putri_cleaned.csv               # Clean dataset hasil olahan
│
├── ide_1_dashboard/                         # SISTEM 1: KATALOG & FILTER
│   ├── app.py                               # Web app katalog interaktif
│   ├── main.ipynb                           # Notebook cleaning & profiling
│   └── README.md                            # Dokumentasi teknis sistem 1
│
├── ide_2_rekomendasi/                       # SISTEM 2: REKOMENDASI PINTAR
│   ├── app_rekomendasi.py                   # Web app pembobotan preferensi
│   ├── rekomendasi.ipynb                    # Notebook formula matematis scoring
│   └── README.md                            # Dokumentasi teknis sistem 2
│
├── ide_3_peta/                              # SISTEM 3: PETA SEBARAN (GEOSPATIAL)
│   ├── app_peta.py                          # Web app visualisasi peta & filter
│   ├── peta.ipynb                           # Notebook geocoding & folium
│   ├── sebaran_kos_map.html                 # Peta interaktif mandiri (HTML)
│   └── README.md                            # Dokumentasi teknis sistem 3
│
├── ide_4_chatbot/                           # SISTEM 4: CHATBOT ASISTEN AI
│   ├── app_chatbot.py                       # Web app chat interface
│   ├── chatbot.ipynb                        # Notebook NLP entity extraction
│   └── README.md                            # Dokumentasi teknis sistem 4
│
├── docs/                                    # Dokumentasi umum sistem
│   └── SISTEM_1_DASHBOARD.md
├── assets/                                  # Gambar pendukung / dokumentasi visual
├── app.py                                   # 🔥 PORTAL TERPADU ALL-IN-ONE (4 Mode Sistem)
├── requirements.txt                         # Daftar pustaka Python yang dibutuhkan
├── .gitignore                               # Konfigurasi file pengabaian Git
└── README.md                                # Dokumentasi utama repositori
```

---

## 🚀 Panduan Memulai (Quickstart)

### 1. Klon Repositori
```bash
git clone https://github.com/<username-anda>/kos-putri-scbd.git
cd kos-putri-scbd
```

### 2. Buat & Aktifkan Virtual Environment (Opsional tapi Disarankan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
Jalankan **Portal Terpadu All-in-One**:
```bash
streamlit run app.py
```
Aplikasi akan terbuka otomatis di peramban Anda pada alamat `http://localhost:8501`.

*(Atau jalankan masing-masing sistem secara mandiri dari foldernya, contoh: `streamlit run ide_4_chatbot/app_chatbot.py`)*

---

## 🛠️ Tech Stack
- **Bahasa:** Python 3.10+
- **Data Manipulation & Analysis:** Pandas, NumPy
- **Interactive Web Framework:** Streamlit
- **Geospatial Visualization:** Folium, OpenStreetMap / CartoDB Positron
- **Text Processing & NLP:** Regular Expressions (Regex)
- **Data Exploration:** Matplotlib, Seaborn, Jupyter Notebook

---

## 📄 Lisensi & Kontribusi
Proyek ini dibuat untuk keperluan edukasi, analisis data terbuka, serta portofolio data science. Kontribusi, isu, dan saran pengembangan sangat dipersilakan!
