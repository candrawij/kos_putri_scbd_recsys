import streamlit as st
import pandas as pd
import numpy as np
import re

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Portal Terpadu Kos Putri SCBD",
    page_icon="🏘️",
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
    .recom-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        border-left: 6px solid #0f766e;
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
    .score-badge {
        background-color: #0f766e;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 700;
        display: inline-block;
    }
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
    try:
        df = pd.read_csv("kost_putri_cleaned.csv")
    except Exception:
        df = pd.read_csv("data/kost_putri_cleaned.csv")
        
    AREA_COORDS = {
        'kledokan': (-7.7765, 110.4095),
        'puluhdadi': (-7.7715, 110.4080),
        'ngropoh': (-7.7665, 110.4070),
        'condongcatur': (-7.7630, 110.4050),
        'dabag': (-7.7680, 110.3995),
        'seturan': (-7.7735, 110.4088)
    }
    DEFAULT_CENTER = (-7.7745, 110.4085)

    def assign_coords(row):
        text = (str(row.get('Alamat', '')) + " " + str(row.get('Nama Kos', ''))).lower()
        base_lat, base_lng = DEFAULT_CENTER
        for area, (lat, lng) in AREA_COORDS.items():
            if area in text:
                base_lat, base_lng = lat, lng
                break
        np.random.seed(int(row.get('No.', 1)) + 42)
        return pd.Series([
            base_lat + np.random.uniform(-0.0020, 0.0020),
            base_lng + np.random.uniform(-0.0020, 0.0020)
        ], index=['latitude', 'longitude'])

    df[['latitude', 'longitude']] = df.apply(assign_coords, axis=1)

    def get_color(harga):
        if pd.isna(harga): return 'gray'
        elif harga < 800000: return 'green'
        elif harga <= 1200000: return 'orange'
        else: return 'red'

    df['marker_color'] = df['harga_min'].apply(get_color)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()

# ---------------- NAVIGATION ----------------
st.sidebar.title("🧭 Mode Sistem")
app_mode = st.sidebar.radio(
    "Pilih Fitur:",
    [
        "🏠 Katalog & Filter Pencarian (Ide 1)",
        "🎯 Rekomendasi Pintar (Ide 2)",
        "🗺️ Peta Sebaran Interaktif (Ide 3)",
        "🤖 Chatbot Asisten Kos (Ide 4)"
    ]
)
st.sidebar.markdown("---")

# ==============================================================================
# MODE 1: KATALOG & FILTER (IDE 1)
# ==============================================================================
if app_mode == "🏠 Katalog & Filter Pencarian (Ide 1)":
    st.title("🏠 Direktori & Pencarian Kos Putri SCBD")
    st.caption("Pencarian katalog interaktif dengan filter fleksibel di area Seturan dan sekitarnya.")

    st.sidebar.header("🔍 Filter Pencarian")
    keyword = st.sidebar.text_input("Cari nama kos atau alamat", placeholder="Contoh: Asri, Kledokan...")

    st.sidebar.subheader("Fasilitas Wajib")
    filter_ac = st.sidebar.checkbox("❄️ AC")
    filter_km_dalam = st.sidebar.checkbox("🚿 Kamar Mandi Dalam")
    filter_wifi = st.sidebar.checkbox("📶 Wi-Fi")
    filter_listrik = st.sidebar.checkbox("⚡ Termasuk Listrik")

    st.sidebar.subheader("Rentang Biaya Per Bulan")
    min_price = int(df['harga_min'].dropna().min()) if not df['harga_min'].dropna().empty else 400000
    max_price = int(df['harga_max'].dropna().max()) if not df['harga_max'].dropna().empty else 2500000

    budget_range = st.sidebar.slider(
        "Rentang Budget (Rp)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=50000,
        format="Rp %d"
    )
    include_unpriced = st.sidebar.checkbox("Sertakan kos tanpa data harga (tanya pemilik)", value=True)

    filtered_df = df.copy()
    if keyword:
        q = keyword.lower().strip()
        filtered_df = filtered_df[
            filtered_df['Nama Kos'].str.lower().str.contains(q, na=False) |
            filtered_df['Alamat'].str.lower().str.contains(q, na=False) |
            filtered_df['Fasilitas Kos'].str.lower().str.contains(q, na=False)
        ]
    if filter_ac: filtered_df = filtered_df[filtered_df['has_ac'] == True]
    if filter_km_dalam: filtered_df = filtered_df[filtered_df['has_km_dalam'] == True]
    if filter_wifi: filtered_df = filtered_df[filtered_df['has_wifi'] == True]
    if filter_listrik: filtered_df = filtered_df[filtered_df['has_listrik'] == True]

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
    tab_cards, tab_table = st.tabs(["📋 Kartu Katalog Kos", "📊 Tabel Data Lengkap"])
    with tab_cards:
        if len(filtered_df) == 0:
            st.warning("Tidak ada kos yang cocok dengan kriteria filter.")
        else:
            cols = st.columns(2)
            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                with cols[idx % 2]:
                    if pd.notna(row.get('harga_min')):
                        if row['harga_min'] == row['harga_max']:
                            harga_str = f"Rp {int(row['harga_min']):,}".replace(",", ".") + " / bulan"
                        else:
                            harga_str = f"Rp {int(row['harga_min']):,} - {int(row['harga_max']):,}".replace(",", ".") + " / bulan"
                    else:
                        harga_str = "Hubungi Pemilik untuk Harga"

                    badges_html = ""
                    if row.get('has_ac'): badges_html += '<span class="badge badge-ac">❄️ AC</span>'
                    if row.get('has_km_dalam'): badges_html += '<span class="badge badge-km">🚿 KM Dalam</span>'
                    if row.get('has_wifi'): badges_html += '<span class="badge badge-wifi">📶 Wi-Fi</span>'
                    if row.get('has_listrik'): badges_html += '<span class="badge badge-listrik">⚡ Listrik</span>'

                    action_html = ""
                    if pd.notna(row.get('wa_url')):
                        msg = f"Halo, saya melihat info {row['Nama Kos']} dari katalog. Apakah masih ada kamar kosong?"
                        action_html += f'<a class="btn-action btn-wa" href="{row["wa_url"]}?text={msg.replace(" ", "%20")}" target="_blank">💬 Chat WhatsApp</a>'
                    if pd.notna(row.get('maps_url')):
                        action_html += f'<a class="btn-action btn-maps" href="{row["maps_url"]}" target="_blank">📍 Google Maps</a>'

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
        st.dataframe(filtered_df[['Nama Kos', 'Biaya Perbulan/semester', 'Alamat', 'Fasilitas Kos', 'Kontak Kos']], use_container_width=True)
        st.download_button("📥 Download Filtered CSV", filtered_df.to_csv(index=False).encode('utf-8'), "kos_filtered.csv", "text/csv")

# ==============================================================================
# MODE 2: REKOMENDASI PINTAR (IDE 2)
# ==============================================================================
elif app_mode == "🎯 Rekomendasi Pintar (Ide 2)":
    st.title("🎯 Sistem Rekomendasi Kos Putri Cerdas")
    st.caption("Pencocokan cerdas berbasis preferensi bobot prioritas dan budget dengan skor persentase kecocokan.")

    st.sidebar.header("📋 Profil Preferensi Anda")
    user_budget = st.sidebar.slider("Target Budget (Rp)", 400000, 2500000, 850000, 50000, format="Rp %d")
    budget_tolerance = st.sidebar.slider("Toleransi Kelebihan Budget (Rp)", 0, 500000, 200000, 50000, format="Rp %d")

    st.sidebar.subheader("Prioritas Fasilitas")
    w_map = {"Tidak Butuh (0)": 0, "Biasa (1)": 1, "Penting (2)": 2, "Wajib/Sangat Penting (3)": 3}
    w_km = w_map[st.sidebar.selectbox("🚿 Kamar Mandi Dalam", list(w_map.keys()), index=3)]
    w_wifi = w_map[st.sidebar.selectbox("📶 Wi-Fi", list(w_map.keys()), index=2)]
    w_ac = w_map[st.sidebar.selectbox("❄️ AC", list(w_map.keys()), index=0)]
    w_listrik = w_map[st.sidebar.selectbox("⚡ Termasuk Listrik", list(w_map.keys()), index=1)]

    st.sidebar.subheader("Preferensi Lokasi")
    loc_opts = ["Kledokan", "Seturan", "Ngropoh", "Condongcatur", "Puluhdadi", "Dabag"]
    sel_locs = st.sidebar.multiselect("Area Prioritas", options=loc_opts, default=["Kledokan"])
    top_k = st.sidebar.slider("Jumlah Rekomendasi Ditampilkan", 3, 15, 5)

    def calculate_price_score(harga, budget, tol):
        if pd.isna(harga): return 0.5
        if harga <= budget: return 1.0
        diff = harga - budget
        return max(0.0, 1.0 - (diff / tol)) if diff <= tol else 0.0

    def calculate_facility_score(row, weights):
        tot = sum(weights.values())
        if tot == 0: return 1.0
        earned = sum(w for f, w in weights.items() if row.get(f) is True)
        return earned / tot

    def calculate_loc_score(row, locs):
        if not locs: return 1.0
        txt = (str(row.get('Alamat', '')) + " " + str(row.get('Nama Kos', ''))).lower()
        return min(1.0, sum(1 for l in locs if l.lower() in txt) / len(locs))

    weights = {'has_km_dalam': w_km, 'has_wifi': w_wifi, 'has_ac': w_ac, 'has_listrik': w_listrik}
    recom_results = []

    for _, row in df.iterrows():
        p_sc = calculate_price_score(row['harga_min'], user_budget, budget_tolerance)
        f_sc = calculate_facility_score(row, weights)
        l_sc = calculate_loc_score(row, sel_locs)
        total = ((p_sc * 0.40) + (f_sc * 0.45) + (l_sc * 0.15)) * 100

        recom_results.append({
            'Nama Kos': row['Nama Kos'],
            'Match Score': round(total, 1),
            'Biaya': row['Biaya Perbulan/semester'],
            'Alamat': row['Alamat'],
            'Fasilitas': row['Fasilitas Kos'],
            'wa_url': row.get('wa_url'),
            'maps_url': row.get('maps_url'),
            'Skor Harga': round(p_sc * 100, 1),
            'Skor Fasilitas': round(f_sc * 100, 1),
            'Skor Lokasi': round(l_sc * 100, 1)
        })

    top_df = pd.DataFrame(recom_results).sort_values(by='Match Score', ascending=False).head(top_k)

    st.subheader(f"✨ Top {top_k} Kos Rekomendasi Terbaik")
    for rank, (_, item) in enumerate(top_df.iterrows(), start=1):
        action_html = ""
        if pd.notna(item['wa_url']):
            msg = f"Halo, saya melihat rekomendasi {item['Nama Kos']} dengan skor kecocokan {item['Match Score']}%. Apakah masih ada kamar kosong?"
            action_html += f'<a class="btn-action btn-wa" href="{item["wa_url"]}?text={msg.replace(" ", "%20")}" target="_blank">💬 Chat WhatsApp</a>'
        if pd.notna(item['maps_url']):
            action_html += f'<a class="btn-action btn-maps" href="{item["maps_url"]}" target="_blank">📍 Google Maps</a>'

        harga_disp = item['Biaya'] if pd.notna(item['Biaya']) and str(item['Biaya']).strip() != '-' else "Hubungi Pemilik"

        st.markdown(f"""
        <div class="recom-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h3 style="margin:0; color:#1e293b;">#{rank} {item['Nama Kos']}</h3>
                <span class="score-badge">Kecocokan: {item['Match Score']}%</span>
            </div>
            <p style="font-size:16px; font-weight:700; color:#0f766e; margin-bottom:6px;">💰 {harga_disp}</p>
            <p style="font-size:13px; color:#475569; margin-bottom:4px;"><b>📍 Alamat:</b> {item['Alamat']}</p>
            <p style="font-size:13px; color:#475569; margin-bottom:8px;"><b>✨ Fasilitas:</b> {item['Fasilitas']}</p>
            <div style="font-size:12px; color:#64748b; margin-top:6px; margin-bottom:6px;">
                Rincian: Harga <b>{item['Skor Harga']}%</b> | Fasilitas <b>{item['Skor Fasilitas']}%</b> | Lokasi <b>{item['Skor Lokasi']}%</b>
            </div>
            <div>{action_html}</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# MODE 3: PETA SEBARAN INTERAKTIF (IDE 3)
# ==============================================================================
elif app_mode == "🗺️ Peta Sebaran Interaktif (Ide 3)":
    st.title("🗺️ Peta Interaktif Sebaran Kos Putri SCBD")
    st.caption("Eksplorasi visual titik kos di sekitar kampus UPN Veteran, STIE YKPN, dan Atma Jaya Babarsari.")

    try:
        import folium
        from streamlit.components.v1 import html
    except ImportError:
        st.error("⚠️ Pustaka `folium` belum terpasang di environment Python Anda.")
        st.info("Silakan buka terminal dan jalankan: `pip install folium` lalu refresh halaman ini.")
        st.stop()

    st.sidebar.header("🔍 Filter Tampilan Peta")
    map_f_ac = st.sidebar.checkbox("❄️ Hanya yang ada AC")
    map_f_km = st.sidebar.checkbox("🚿 Hanya yang ada KM Dalam")
    map_f_wifi = st.sidebar.checkbox("📶 Hanya yang ada Wi-Fi")

    map_kategori_harga = st.sidebar.multiselect(
        "Kategori Rentang Biaya",
        options=["< Rp800.000 (Hijau)", "Rp800.000 - Rp1.200.000 (Kuning)", "> Rp1.200.000 (Merah)", "Tanya Pemilik (Abu-abu)"],
        default=["< Rp800.000 (Hijau)", "Rp800.000 - Rp1.200.000 (Kuning)", "> Rp1.200.000 (Merah)", "Tanya Pemilik (Abu-abu)"]
    )

    color_map = {
        "< Rp800.000 (Hijau)": "green",
        "Rp800.000 - Rp1.200.000 (Kuning)": "orange",
        "> Rp1.200.000 (Merah)": "red",
        "Tanya Pemilik (Abu-abu)": "gray"
    }
    sel_colors = [color_map[k] for k in map_kategori_harga]

    map_df = df[df['marker_color'].isin(sel_colors)]
    if map_f_ac: map_df = map_df[map_df['has_ac'] == True]
    if map_f_km: map_df = map_df[map_df['has_km_dalam'] == True]
    if map_f_wifi: map_df = map_df[map_df['has_wifi'] == True]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kos Ditampilkan", f"{len(map_df)} Titik")
    c2.metric("🟢 < 800rb", f"{len(map_df[map_df['marker_color'] == 'green'])}")
    c3.metric("🟡 800rb - 1.2jt", f"{len(map_df[map_df['marker_color'] == 'orange'])}")
    c4.metric("🔴 > 1.2jt", f"{len(map_df[map_df['marker_color'] == 'red'])}")

    m = folium.Map(location=[-7.7720, 110.4080], zoom_start=14, tiles="CartoDB positron")

    CAMPUS_LANDMARKS = [
        {"name": "STIE YKPN Yogyakarta", "coords": [-7.7755, 110.4078], "color": "darkblue"},
        {"name": "UPN Veteran Kampus 1", "coords": [-7.7618, 110.4086], "color": "darkblue"},
        {"name": "UAJY Kampus 3 Babarsari", "coords": [-7.7797, 110.4158], "color": "purple"}
    ]
    for camp in CAMPUS_LANDMARKS:
        folium.Marker(
            location=camp["coords"],
            popup=folium.Popup(f"<b>🎓 {camp['name']}</b>", max_width=250),
            tooltip=f"Kampus: {camp['name']}",
            icon=folium.Icon(color=camp["color"], icon="graduation-cap", prefix="fa")
        ).add_to(m)

    for _, row in map_df.iterrows():
        harga_lbl = f"Rp {int(row['harga_min']):,} / bln".replace(",", ".") if pd.notna(row['harga_min']) else "Tanya Pemilik"
        fac_badges = ""
        if row.get('has_ac'): fac_badges += "❄️ AC "
        if row.get('has_km_dalam'): fac_badges += "🚿 KM Dalam "
        if row.get('has_wifi'): fac_badges += "📶 Wi-Fi "
        if not fac_badges: fac_badges = "Standar"

        wa_btn = ""
        if pd.notna(row.get('wa_url')):
            wa_btn = f"<br><a href='{row['wa_url']}' target='_blank' style='display:inline-block; margin-top:6px; background:#25D366; color:white; padding:4px 8px; border-radius:4px; text-decoration:none; font-size:11px;'>💬 Chat WA</a>"

        popup_html = f"""
        <div style='font-family:sans-serif; width:200px;'>
            <h4 style='margin:0 0 5px 0;'>{row['Nama Kos']}</h4>
            <p style='margin:0; font-weight:bold; color:#0f766e;'>💰 {harga_lbl}</p>
            <p style='margin:4px 0; font-size:11px;'><b>📍</b> {row['Alamat'][:50]}...</p>
            <p style='margin:4px 0; font-size:11px;'><b>✨</b> {fac_badges}</p>
            {wa_btn}
        </div>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{row['Nama Kos']} ({harga_lbl})",
            icon=folium.Icon(color=row['marker_color'], icon="home")
        ).add_to(m)

    map_html = m._repr_html_()
    html(map_html, height=600)

# ==============================================================================
# MODE 4: CHATBOT ASISTEN KOS (IDE 4)
# ==============================================================================
else:
    st.title("🤖 Chatbot Asisten Kos Putri SCBD")
    st.caption("Tanyakan kos idaman Anda dengan bahasa santai. Asisten otomatis memfilter dan merangkumkan pilihan terbaik.")

    def parse_user_query(query_text):
        text = query_text.lower()
        criteria = {'max_budget': None, 'facilities': {}, 'location': None}
        
        juta_match = re.search(r'(\d+[\.,]?\d*)\s*(juta|jt)', text)
        if juta_match:
            val = float(juta_match.group(1).replace(',', '.'))
            criteria['max_budget'] = int(val * 1000000)
        else:
            rb_match = re.search(r'(\d+)\s*(rb|ribu)', text)
            if rb_match:
                criteria['max_budget'] = int(rb_match.group(1)) * 1000
            else:
                raw_nums = re.findall(r'\d{6,}', text.replace('.', ''))
                if raw_nums: criteria['max_budget'] = int(raw_nums[0])

        if re.search(r'\bac\b|air conditioner', text): criteria['facilities']['has_ac'] = True
        if re.search(r'km dalam|kamar mandi dalam|kamar mandi', text): criteria['facilities']['has_km_dalam'] = True
        if re.search(r'wifi|wi-fi|internet', text): criteria['facilities']['has_wifi'] = True
        if re.search(r'listrik', text): criteria['facilities']['has_listrik'] = True

        known_areas = ['kledokan', 'seturan', 'ngropoh', 'condongcatur', 'puluhdadi', 'dabag', 'upn', 'ykpn']
        for area in known_areas:
            if area in text:
                criteria['location'] = area
                break
        return criteria

    def generate_bot_response(user_message, df_source, top_n=3):
        criteria = parse_user_query(user_message)
        max_budget = criteria['max_budget']
        facs = criteria['facilities']
        loc = criteria['location']
        
        candidate_df = df_source.copy()
        if loc:
            candidate_df = candidate_df[
                candidate_df['Alamat'].str.lower().str.contains(loc, na=False) |
                candidate_df['Nama Kos'].str.lower().str.contains(loc, na=False)
            ]
        for fac_col, required in facs.items():
            if required: candidate_df = candidate_df[candidate_df[fac_col] == True]
        if max_budget:
            candidate_df = candidate_df[
                (candidate_df['harga_min'].isna()) | (candidate_df['harga_min'] <= max_budget)
            ]

        candidate_df = candidate_df.sort_values(by='harga_min', ascending=True, na_position='last')

        if candidate_df.empty:
            return (
                f"Maaf kak, belum ada kos yang cocok persis dengan kriteria tersebut "
                f"(Budget: Rp{max_budget:, if max_budget else '-'}, Fasilitas: {list(facs.keys())}, Lokasi: {loc}).\n\n"
                f"💡 *Saran:* Coba naikkan rentang budget sedikit atau kurangi salah satu fasilitas wajib."
            )

        filter_notes = []
        if loc: filter_notes.append(f"di sekitar **{loc.title()}**")
        if facs: 
            fac_labels = [k.replace('has_', '').replace('_', ' ').upper() for k in facs.keys()]
            filter_notes.append(f"fasilitas **{', '.join(fac_labels)}**")
        if max_budget: filter_notes.append(f"budget maksimal **Rp {max_budget:,}**".replace(",", "."))
        
        catatan = ", ".join(filter_notes) if filter_notes else "semua kriteria"
        res = [f"Halo kak! Berdasarkan pencarian untuk {catatan}, ini ada **{min(len(candidate_df), top_n)} pilihan kos terbaik**:\n"]

        for i, (_, row) in enumerate(candidate_df.head(top_n).iterrows(), start=1):
            if pd.notna(row['harga_min']):
                if row['harga_min'] == row['harga_max']:
                    harga_txt = f"Rp {int(row['harga_min']):,} / bulan".replace(",", ".")
                else:
                    harga_txt = f"Rp {int(row['harga_min']):,} - {int(row['harga_max']):,} / bulan".replace(",", ".")
            else:
                harga_txt = "Hubungi pemilik untuk harga"

            wa_link = f"[💬 Chat WhatsApp]({row['wa_url']})" if pd.notna(row.get('wa_url')) else ""
            maps_link = f"[📍 Google Maps]({row['maps_url']})" if pd.notna(row.get('maps_url')) else ""

            res.append(
                f"**{i}. {row['Nama Kos']}**\n"
                f"- 💰 **Harga:** {harga_txt}\n"
                f"- 📍 **Alamat:** {row['Alamat'][:65]}...\n"
                f"- ✨ **Fasilitas:** {row['Fasilitas Kos']}\n"
                f"- 📲 **Aksi:** {wa_link}  {maps_link}\n"
            )
        res.append("Ada lagi kriteria kos yang ingin kakak tanyakan?")
        return "\n".join(res)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Halo! 👋 Saya asisten pintar pencari kos putri SCBD.\n\n"
                    "Kakak bisa langsung tanyakan seperti:\n"
                    "- *'Ada kos di Kledokan yang ada AC budget 1 juta?'*\n"
                    "- *'Cari kos murah di Seturan yang ada kamar mandi dalam dan wifi dong'*."
                )
            }
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tulis pertanyaan pencarian kos di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = generate_bot_response(prompt, df)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
