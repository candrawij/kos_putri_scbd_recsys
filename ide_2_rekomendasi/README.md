# Dokumentasi Proyek: Sistem 2 - Content-Based Recommendation Engine
**Dataset:** Direktori Kos Putri SCBD  
**Teknologi:** Python, Pandas, NumPy, Streamlit

---

## 1. Konsep & Perbedaan dengan Sistem 1
Pada **Sistem 1 (Katalog & Filter)**, sistem bekerja dengan logika boolean kaku (*hard filter*):
- Jika budget Rp800.000, maka kos dengan harga Rp850.000 langsung dibuang dari hasil, meskipun fasilitas dan lokasinya sangat cocok.

Pada **Sistem 2 (Recommendation Engine)**, sistem menggunakan pendekatan *soft matching* dengan **Content-Based Filtering**:
- Kos tidak langsung dibuang, melainkan diberikan nilai kecocokan (*Match Score* 0 - 100%).
- Pengguna dapat menentukan tingkat prioritas/bobot untuk tiap fasilitas (Wajib, Penting, Biasa, atau Tidak Butuh).
- Sistem menghitung trade-off antara harga, fasilitas, dan kedekatan lokasi.

---

## 2. Formulasi Matematis

Total skor kecocokan kos dihitung menggunakan rumus pembobotan multikriteria:

$$\text{Total Match Score} = \left( w_p \cdot S_{\text{harga}} + w_f \cdot S_{\text{fasilitas}} + w_l \cdot S_{\text{lokasi}} \right) \times 100\%$$

Di mana:
- Bobot Komponen: $w_p = 0.40$ (Harga), $w_f = 0.45$ (Fasilitas), $w_l = 0.15$ (Lokasi).

### A. Skor Harga ($S_{\text{harga}}$)
$$S_{\text{harga}} = 
\begin{cases} 
1.0 & \text{jika } \text{Harga} \le \text{Budget} \\
\max\left(0, 1 - \frac{\text{Harga} - \text{Budget}}{\text{Toleransi}}\right) & \text{jika } \text{Harga} > \text{Budget} \\
0.5 & \text{jika harga belum terdata (netral)}
\end{cases}$$

### B. Skor Fasilitas ($S_{\text{fasilitas}}$)
$$S_{\text{fasilitas}} = \frac{\sum_{i} (\text{Bobot}_i \times \mathbb{I}_{\text{tersedia}})}{\sum_{i} \text{Bobot}_i}$$
Skala bobot: Wajib (3), Penting (2), Biasa (1), Tidak Butuh (0).

### C. Skor Lokasi ($S_{\text{lokasi}}$)
Mencocokkan kemunculan kata kunci area preferensi pengguna pada kolom `Alamat` dan `Nama Kos`.

---

## 3. Struktur File
```
ide_2_rekomendasi/
├── rekomendasi.ipynb    # Eksplorasi & pengujian algoritma secara matematis
├── app_rekomendasi.py   # Web UI mandiri untuk sistem rekomendasi
└── README.md            # Dokumentasi teknis sistem 2
```

## 4. Cara Menjalankan
Jalankan aplikasi rekomendasi mandiri:
```bash
streamlit run ide_2_rekomendasi/app_rekomendasi.py
```
