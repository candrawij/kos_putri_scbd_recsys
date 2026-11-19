# Dokumentasi Proyek: Sistem 1 - Interactive Web Dashboard & Search Catalog
**Dataset:** Direktori Kos Putri SCBD (Seturan, Caturtunggal, Condongcatur, Sleman, DIY)  
**Teknologi:** Python, Pandas, Streamlit, Regular Expressions (Regex)

---

## 1. Latar Belakang & Masalah
Dataset awal (`KOST PUTRI SCBD - Kost Putri.csv`) merupakan data survei riil kos putri di sekitar kampus area Babarsari - Seturan (SCBD). Data mentah ini memiliki beberapa karakteristik dan tantangan data:
- **Header Bergeser:** Terdapat baris kosong pada baris pertama CSV sehingga header terbaca sebagai `Unnamed: 0`, dst.
- **Teks Harga Tidak Terstandarisasi:** Harga tercampur dengan teks deskriptif (contoh: `"Rp750.000-1.200.000/bulan (sesuai tipe kamar)"`).
- **Fasilitas Berupa Free-text:** Tidak berupa kategori diskrit melainkan paragraf atau daftar teks yang tidak seragam.
- **Tautan Kontak & Lokasi:** Format WhatsApp bervariasi (`wa.me//...`, nomor lokal `08...`, format internasional) dan tautan Google Maps ada yang berupa URL pendek, teks query, atau kosong.
- **Data Kosong (Missing Values):** Beberapa baris tidak memiliki nama kos eksplisit atau belum memiliki data biaya.

---

## 2. Tahapan Rekayasa Data (Data Pipeline)

### A. Preprocessing & Data Cleaning
1. **Perbaikan Pembacaan Header:**
   Menggunakan `header=1` pada `pd.read_csv` untuk melewati baris kosong awal.
2. **Penanganan Missing Values pada Nama Kos:**
   Semua 63 baris data dipertahankan. Baris yang tidak memiliki `Nama Kos` diberikan label otomatis: `Kos Putri (No. X)` agar kontak dan lokasinya tetap dapat diakses pengguna.
3. **Pembersihan Kolom:**
   Menghapus 3 kolom yang 100% kosong: `Nama Rekomendasi`, `Jurusan Rekomendasi`, dan `Kontak`.
4. **Pembersihan Karakter:**
   Menghilangkan karakter *newline* (`\n`) dan spasi berlebih pada kolom teks agar tampilan rapi.

### B. Feature Engineering
1. **Ekstraksi Rentang Harga (`harga_min` & `harga_max`):**
   Menggunakan regex untuk mengekstrak angka numerik minimal 6 digit (ratusan ribu/jutaan rupiah). Menghasilkan dua variabel numerik:
   - `harga_min`: Batas bawah harga kamar (tipe termurah).
   - `harga_max`: Batas atas harga kamar (tipe tertinggi/AC).
2. **Deteksi Fasilitas Cerdas (Boolean Flags):**
   Mendeteksi fitur penting dengan menggabungkan teks dari kolom `Fasilitas Kos` dan `Biaya Perbulan/semester` (karena opsi seperti AC sering kali tertulis di deskripsi harga/tipe kamar):
   - `has_ac`: Deteksi AC / Air Conditioner.
   - `has_km_dalam`: Deteksi Kamar Mandi Dalam.
   - `has_wifi`: Deteksi Wi-Fi / Internet.
   - `has_kasur`: Deteksi Kasur / Springbed.
   - `has_listrik`: Deteksi apakah biaya sudah termasuk listrik.
3. **Standarisasi Link WhatsApp (`wa_url`):**
   Mengekstrak nomor telepon dan mengonversi format ke standar internasional `https://wa.me/62...`.
4. **Standarisasi Link Google Maps (`maps_url`):**
   Memastikan format tautan valid; jika hanya berisi teks nama tempat/kode plus, diubah ke URL Google Maps Search API (`https://www.google.com/maps/search/?api=1&query=...`).

---

## 3. Arsitektur Sistem Dashboard (`app.py`)

Aplikasi web dibangun menggunakan **Streamlit** dengan komponen:

### A. Komponen Antarmuka (UI/UX)
- **Sidebar Kontrol:**
  - *Pencarian Fleksibel:* Mencari berdasarkan kata kunci pada nama kos, alamat, atau fasilitas.
  - *Checkbox Fasilitas:* Memilih kombinasi fasilitas wajib (AC, KM Dalam, Wi-Fi, Listrik).
  - *Budget Slider:* Mengatur rentang harga minimum dan maksimum per bulan.
  - *Toggle Kos Tanpa Harga:* Opsi untuk tetap menampilkan kos yang belum mencantumkan harga (untuk ditanyakan langsung).
- **Sortir Data (Sorting Control):**
  - Rekomendasi (Default)
  - Harga: Termurah ke Tertinggi
  - Harga: Tertinggi ke Termurah
  - Nama Kos (A-Z)
- **Metrik Real-time:** Menampilkan total kos hasil filter, harga termurah, rata-rata, dan harga tertinggi.
- **Kartu Katalog Kos (Grid Card):** Menampilkan kos dalam bentuk kartu informatif lengkap dengan badge fasilitas, alamat, serta dua tombol aksi:
  - 💬 **Chat WhatsApp:** Membuka WhatsApp pemilik kos dengan template pesan otomatis:  
    *"Halo, saya melihat info [Nama Kos] dari katalog. Apakah masih ada kamar kosong?"*
  - 📍 **Google Maps:** Membuka titik lokasi kos langsung di Google Maps.
- **Tab Tabel & Ekspor:** Menampilkan data tabel tabular lengkap dan tombol unduh data terfilter (`.csv`).

---

## 4. Struktur Folder Proyek

```
Kos putri SCBD/
│
├── data/                                # Penyimpanan data mentah & hasil olahan
│   ├── KOST PUTRI SCBD - Kost Putri.csv # Raw dataset asli
│   └── kost_putri_cleaned.csv           # Cleaned dataset hasil pipeline
│
├── docs/                                # Dokumentasi sistem & panduan
│   └── SISTEM_1_DASHBOARD.md            # Dokumentasi lengkap sistem 1
│
├── assets/                              # Gambar, tangkapan layar, atau aset grafis
│   └── Screenshot 2026-11-18 164213.png
│
├── main.ipynb                           # Jupyter Notebook eksplorasi & pipeline data
├── app.py                               # Skrip aplikasi Streamlit (Web Dashboard)
├── kost_putri_cleaned.csv               # Simlink / salinan root untuk kemudahan runner
└── KOST PUTRI SCBD - Kost Putri.csv     # Salinan root
```

---

## 5. Cara Menjalankan Aplikasi

1. Buka terminal di folder proyek ini:
   ```bash
   cd "e:\DataScience\Kos putri SCBD"
   ```
2. Pastikan dependensi sudah terpasang:
   ```bash
   pip install pandas streamlit
   ```
3. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run app.py
   ```
4. Buka peramban (browser) di alamat yang muncul di terminal (biasanya `http://localhost:8501`).
