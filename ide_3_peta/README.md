# Dokumentasi Proyek: Sistem 3 - Geospatial Mapping (Peta Sebaran Interaktif)
**Dataset:** Direktori Kos Putri SCBD  
**Teknologi:** Python, Pandas, Folium, OpenStreetMap (CartoDB Positron), Streamlit

---

## 1. Konsep & Fitur
Sistem ini menyediakan visualisasi geospasial interaktif yang memetakan seluruh kos putri di daerah Seturan/Babarsari (SCBD):
1. **Penanda Kampus Utama (Landmark):**
   - STIE YKPN Yogyakarta
   - UPN "Veteran" Yogyakarta (Kampus Condongcatur)
   - Universitas Atma Jaya Yogyakarta (UAJY Kampus 3 Babarsari)
2. **Kategori Pewarnaan Berbasis Harga:**
   - 🟢 **Hijau:** < Rp800.000 / bulan (Ramah kantong)
   - 🟡 **Kuning/Oranye:** Rp800.000 - Rp1.200.000 / bulan (Menengah)
   - 🔴 **Merah:** > Rp1.200.000 / bulan (Premium / Eksklusif)
   - ⚪ **Abu-abu:** Belum tercatat / Hubungi pemilik
3. **Popup Interaktif:**
   - Mengklik pin kos memunculkan nama, harga, alamat, fasilitas, dan tombol cepat WhatsApp.

---

## 2. Struktur File
```
ide_3_peta/
├── peta.ipynb             # Notebook eksperimen geocoding & visualisasi Folium
├── sebaran_kos_map.html   # File peta interaktif mandiri (dapat dibuka langsung di browser)
├── app_peta.py            # Web UI interaktif peta dengan filter dinamis
└── README.md              # Dokumentasi teknis sistem 3
```

## 3. Cara Menjalankan
Jalankan aplikasi peta mandiri:
```bash
streamlit run ide_3_peta/app_peta.py
```
Atau cukup buka file `sebaran_kos_map.html` di Google Chrome/Edge.
