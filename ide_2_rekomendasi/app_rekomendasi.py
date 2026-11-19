import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Sistem Rekomendasi Kos Putri Cerdas",
    page_icon="🎯",
    layout="wide"
)

# Styling
st.markdown("""
<style>
    .recom-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        border-left: 6px solid #0f766e;
    }
    .score-badge {
        background-color: #0f766e;
        color: white;
        padding: 6px 12px;
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
    }
    .btn-wa { background-color: #25D366; color: white !important; }
    .btn-maps { background-color: #4285F4; color: white !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("data/kost_putri_cleaned.csv")

try:
    df = load_data()
except Exception:
    df = pd.read_csv("../data/kost_putri_cleaned.csv")

st.title("🎯 Sistem Rekomendasi Kos Putri Cerdas")
st.caption("Gunakan algoritma pembobotan cerdas (*Content-Based Filtering*) untuk menemukan kos yang paling sesuai dengan preferensi & budget Anda.")

# ---------------- FORM INPUT PREFERENSI ----------------
st.sidebar.header("📋 Profil Preferensi Anda")

# 1. Budget
st.sidebar.subheader("1. Budget Bulanan")
user_budget = st.sidebar.slider(
    "Target Budget (Rp)",
    min_value=400000,
    max_value=2500000,
    value=850000,
    step=50000,
    format="Rp %d"
)
budget_tolerance = st.sidebar.slider(
    "Toleransi Kelebihan Budget (Rp)",
    min_value=0,
    max_value=500000,
    value=200000,
    step=50000,
    format="Rp %d",
    help="Batas maksimal kelebihan harga yang masih ingin Anda pertimbangkan."
)

# 2. Bobot Fasilitas
st.sidebar.subheader("2. Prioritas Fasilitas")
weight_map = {"Tidak Butuh (0)": 0, "Biasa (1)": 1, "Penting (2)": 2, "Wajib/Sangat Penting (3)": 3}

w_km = weight_map[st.sidebar.selectbox("🚿 Kamar Mandi Dalam", list(weight_map.keys()), index=3)]
w_wifi = weight_map[st.sidebar.selectbox("📶 Wi-Fi", list(weight_map.keys()), index=2)]
w_ac = weight_map[st.sidebar.selectbox("❄️ AC", list(weight_map.keys()), index=0)]
w_listrik = weight_map[st.sidebar.selectbox("⚡ Termasuk Listrik", list(weight_map.keys()), index=1)]

# 3. Preferensi Lokasi
st.sidebar.subheader("3. Preferensi Lokasi")
location_options = ["Kledokan", "Seturan", "Ngropoh", "Condongcatur", "Puluhdadi", "Dabag"]
selected_locations = st.sidebar.multiselect(
    "Area Prioritas",
    options=location_options,
    default=["Kledokan"]
)

top_k = st.sidebar.slider("Jumlah Rekomendasi", min_value=3, max_value=15, value=5)

# ---------------- FUNGSI ENGINE ----------------
def calculate_price_score(harga_kos, budget, tolerance):
    if pd.isna(harga_kos):
        return 0.5
    if harga_kos <= budget:
        return 1.0
    diff = harga_kos - budget
    if diff <= tolerance:
        return max(0.0, 1.0 - (diff / tolerance))
    return 0.0

def calculate_facility_score(row, weights):
    total_w = sum(weights.values())
    if total_w == 0:
        return 1.0
    earned = sum(w for feat, w in weights.items() if row.get(feat) is True)
    return earned / total_w

def calculate_location_score(row, locs):
    if not locs:
        return 1.0
    text = (str(row.get('Alamat', '')) + " " + str(row.get('Nama Kos', ''))).lower()
    matches = sum(1 for loc in locs if loc.lower() in text)
    return min(1.0, matches / len(locs))

# Eksekusi Rekomendasi
weights = {'has_km_dalam': w_km, 'has_wifi': w_wifi, 'has_ac': w_ac, 'has_listrik': w_listrik}
results = []

for _, row in df.iterrows():
    p_score = calculate_price_score(row['harga_min'], user_budget, budget_tolerance)
    f_score = calculate_facility_score(row, weights)
    l_score = calculate_location_score(row, selected_locations)
    
    total = ((p_score * 0.40) + (f_score * 0.45) + (l_score * 0.15)) * 100
    
    results.append({
        'Nama Kos': row['Nama Kos'],
        'Match Score': round(total, 1),
        'Biaya': row['Biaya Perbulan/semester'],
        'harga_min': row['harga_min'],
        'Alamat': row['Alamat'],
        'Fasilitas': row['Fasilitas Kos'],
        'wa_url': row.get('wa_url'),
        'maps_url': row.get('maps_url'),
        'Skor Harga': round(p_score * 100, 1),
        'Skor Fasilitas': round(f_score * 100, 1),
        'Skor Lokasi': round(l_score * 100, 1)
    })

res_df = pd.DataFrame(results).sort_values(by='Match Score', ascending=False).head(top_k)

# ---------------- TAMPILAN REKOMENDASI ----------------
st.subheader(f"✨ Top {top_k} Kos Paling Cocok untuk Anda")

for rank, (_, item) in enumerate(res_df.iterrows(), start=1):
    action_html = ""
    if pd.notna(item['wa_url']):
        msg = f"Halo, saya melihat rekomendasi {item['Nama Kos']} dengan kecocokan {item['Match Score']}%. Apakah kamar masih tersedia?"
        action_html += f'<a class="btn-action btn-wa" href="{item["wa_url"]}?text={msg.replace(" ", "%20")}" target="_blank">💬 Chat WhatsApp</a>'
    if pd.notna(item['maps_url']):
        action_html += f'<a class="btn-action btn-maps" href="{item["maps_url"]}" target="_blank">📍 Google Maps</a>'

    harga_display = item['Biaya'] if pd.notna(item['Biaya']) and str(item['Biaya']).strip() != '-' else "Hubungi Pemilik"

    st.markdown(f"""
    <div class="recom-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h3 style="margin:0; color:#1e293b;">#{rank} {item['Nama Kos']}</h3>
            <span class="score-badge">Kecocokan: {item['Match Score']}%</span>
        </div>
        <p style="font-size:16px; font-weight:700; color:#0f766e; margin-bottom:6px;">💰 {harga_display}</p>
        <p style="font-size:13px; color:#475569; margin-bottom:4px;"><b>📍 Alamat:</b> {item['Alamat']}</p>
        <p style="font-size:13px; color:#475569; margin-bottom:8px;"><b>✨ Fasilitas:</b> {item['Fasilitas']}</p>
        <div style="font-size:12px; color:#64748b; margin-top:6px; margin-bottom:6px;">
            Rincian Kecocokan: Harga <b>{item['Skor Harga']}%</b> | Fasilitas <b>{item['Skor Fasilitas']}%</b> | Lokasi <b>{item['Skor Lokasi']}%</b>
        </div>
        <div>{action_html}</div>
    </div>
    """, unsafe_allow_html=True)
