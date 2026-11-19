import streamlit as st
import pandas as pd
import numpy as np

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Katalog & Pencarian Kos Putri SCBD",
    page_icon="🏠",
    layout="wide"
)

# Custom Styling (CSS)
st.markdown("""
<style>
    .kost-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kost-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.1);
    }
    .badge {
        display: inline-block;
        padding: 4px 9px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 6px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-ac { background-color: #dbeafe; color: #1e40af; }
    .badge-km { background-color: #dcfce7; color: #166534; }
    .badge-wifi { background-color: #fef3c7; color: #92400e; }
    .badge-listrik { background-color: #f3e8ff; color: #6b21a8; }
    .btn-action {
        display: inline-block;
        text-decoration: none;
        padding: 7px 15px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
        margin-top: 10px;
        text-align: center;
    }
    .btn-wa { background-color: #25D366; color: white !important; }
    .btn-maps { background-color: #4285F4; color: white !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("kost_putri_cleaned.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()

# Header Utama
st.title("🏠 Direktori & Pencarian Kos Putri SCBD")
st.caption("Platform pencarian terintegrasi kos putri di area Seturan, Caturtunggal, Condongcatur, dan Sleman.")

# ----------------- SIDEBAR FILTER -----------------
st.sidebar.header("🔍 Filter Pencarian")

# 1. Search Bar
keyword = st.sidebar.text_input("Cari nama kos atau alamat", placeholder="Contoh: Asri, Kledokan, Seturan...")

# 2. Filter Fasilitas
st.sidebar.subheader("Fasilitas Wajib")
filter_ac = st.sidebar.checkbox("❄️ AC")
filter_km_dalam = st.sidebar.checkbox("🚿 Kamar Mandi Dalam")
filter_wifi = st.sidebar.checkbox("📶 Wi-Fi")
filter_listrik = st.sidebar.checkbox("⚡ Termasuk Listrik")

# 3. Filter Harga
st.sidebar.subheader("Rentang Biaya Per Bulan")
min_dataset_price = int(df['harga_min'].dropna().min()) if not df['harga_min'].dropna().empty else 400000
max_dataset_price = int(df['harga_max'].dropna().max()) if not df['harga_max'].dropna().empty else 2500000

budget_range = st.sidebar.slider(
    "Rentang Budget (Rp)",
    min_value=min_dataset_price,
    max_value=max_dataset_price,
    value=(min_dataset_price, max_dataset_price),
    step=50000,
    format="Rp %d"
)

include_unpriced = st.sidebar.checkbox("Sertakan kos tanpa data harga (tanya pemilik)", value=True)

# ----------------- LOGIKA FILTERING -----------------
filtered_df = df.copy()

# Filter Keyword
if keyword:
    q = keyword.lower().strip()
    filtered_df = filtered_df[
        filtered_df['Nama Kos'].str.lower().str.contains(q, na=False) |
        filtered_df['Alamat'].str.lower().str.contains(q, na=False) |
        filtered_df['Fasilitas Kos'].str.lower().str.contains(q, na=False)
    ]

# Filter Fasilitas
if filter_ac:
    filtered_df = filtered_df[filtered_df['has_ac'] == True]
if filter_km_dalam:
    filtered_df = filtered_df[filtered_df['has_km_dalam'] == True]
if filter_wifi:
    filtered_df = filtered_df[filtered_df['has_wifi'] == True]
if filter_listrik:
    filtered_df = filtered_df[filtered_df['has_listrik'] == True]

# Filter Harga
if include_unpriced:
    price_mask = (
        (filtered_df['harga_min'].isna()) | 
        ((filtered_df['harga_min'] <= budget_range[1]) & (filtered_df['harga_max'] >= budget_range[0]))
    )
else:
    price_mask = (
        (filtered_df['harga_min'].notna()) & 
        (filtered_df['harga_min'] <= budget_range[1]) & 
        (filtered_df['harga_max'] >= budget_range[0])
    )
filtered_df = filtered_df[price_mask]

# ----------------- KONTROL URUTAN (SORTING) -----------------
col_sort, _ = st.columns([2, 3])
with col_sort:
    sort_option = st.selectbox(
        "Urutkan berdasarkan:",
        ["Rekomendasi (Default)", "Harga: Termurah ke Tertinggi", "Harga: Tertinggi ke Termurah", "Nama Kos (A-Z)"]
    )

if sort_option == "Harga: Termurah ke Tertinggi":
    filtered_df = filtered_df.sort_values(by="harga_min", ascending=True, na_position="last")
elif sort_option == "Harga: Tertinggi ke Termurah":
    filtered_df = filtered_df.sort_values(by="harga_max", ascending=False, na_position="last")
elif sort_option == "Nama Kos (A-Z)":
    filtered_df = filtered_df.sort_values(by="Nama Kos", ascending=True)

# ----------------- STATISTIK RINGKAS -----------------
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("Total Kos Ditemukan", f"{len(filtered_df)} Kos")

valid_prices = filtered_df['harga_min'].dropna()
if not valid_prices.empty:
    col_stat2.metric("Harga Termurah", f"Rp {int(valid_prices.min()):,}".replace(",", "."))
    col_stat3.metric("Rata-rata Harga", f"Rp {int(valid_prices.mean()):,}".replace(",", "."))
    col_stat4.metric("Harga Tertinggi", f"Rp {int(filtered_df['harga_max'].dropna().max()):,}".replace(",", "."))
else:
    col_stat2.metric("Harga Termurah", "-")
    col_stat3.metric("Rata-rata Harga", "-")
    col_stat4.metric("Harga Tertinggi", "-")

st.markdown("---")

# ----------------- TAMPILAN KATALOG KOS -----------------
tab_cards, tab_table = st.tabs(["📋 Kartu Katalog Kos", "📊 Tabel Data Lengkap"])

with tab_cards:
    if len(filtered_df) == 0:
        st.warning("Tidak ada kos yang cocok dengan kriteria filter yang Anda pilih. Coba longgarkan rentang harga atau kurangi filter fasilitas.")
    else:
        # Tampilkan dalam grid 2 kolom
        cols = st.columns(2)
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 2]:
                # Format Teks Harga
                if pd.notna(row.get('harga_min')):
                    if row['harga_min'] == row['harga_max']:
                        harga_str = f"Rp {int(row['harga_min']):,}".replace(",", ".") + " / bulan"
                    else:
                        harga_str = f"Rp {int(row['harga_min']):,} - {int(row['harga_max']):,}".replace(",", ".") + " / bulan"
                else:
                    raw_harga = str(row.get('Biaya Perbulan/semester', '')).strip()
                    harga_str = raw_harga if raw_harga and raw_harga != '-' else "Hubungi Pemilik untuk Harga"

                # Badges Fasilitas
                badges_html = ""
                if row.get('has_ac'):
                    badges_html += '<span class="badge badge-ac">❄️ AC</span>'
                if row.get('has_km_dalam'):
                    badges_html += '<span class="badge badge-km">🚿 KM Dalam</span>'
                if row.get('has_wifi'):
                    badges_html += '<span class="badge badge-wifi">📶 Wi-Fi</span>'
                if row.get('has_listrik'):
                    badges_html += '<span class="badge badge-listrik">⚡ Listrik</span>'

                # Action Buttons
                action_html = ""
                if pd.notna(row.get('wa_url')):
                    pesan_wa = f"Halo, saya melihat info {row['Nama Kos']} dari katalog. Apakah masih ada kamar kosong?"
                    link_wa_final = f"{row['wa_url']}?text={pesan_wa.replace(' ', '%20')}"
                    action_html += f'<a class="btn-action btn-wa" href="{link_wa_final}" target="_blank">💬 Chat WhatsApp</a>'
                
                if pd.notna(row.get('maps_url')):
                    action_html += f'<a class="btn-action btn-maps" href="{row["maps_url"]}" target="_blank">📍 Google Maps</a>'

                # Render Card Container
                st.markdown(f"""
                <div class="kost-card">
                    <div>
                        <h3 style="margin-top:0; color:#1e293b; font-size:18px;">{row['Nama Kos']}</h3>
                        <p style="font-size:16px; font-weight:700; color:#0f766e; margin-bottom:8px;">💰 {harga_str}</p>
                        <p style="font-size:13px; color:#475569; margin-bottom:6px;"><b>📍 Alamat:</b> {row['Alamat']}</p>
                        <p style="font-size:13px; color:#475569; margin-bottom:10px;"><b>✨ Fasilitas:</b> {row['Fasilitas Kos']}</p>
                        <div>{badges_html}</div>
                    </div>
                    <div style="margin-top: 12px;">{action_html}</div>
                </div>
                """, unsafe_allow_html=True)

with tab_table:
    st.dataframe(
        filtered_df[['Nama Kos', 'Biaya Perbulan/semester', 'Alamat', 'Fasilitas Kos', 'Kontak Kos']],
        use_container_width=True
    )
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Hasil Filter (.csv)",
        data=csv_data,
        file_name="kos_filtered.csv",
        mime="text/csv"
    )
