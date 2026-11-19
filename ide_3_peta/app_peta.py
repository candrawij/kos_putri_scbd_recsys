import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Peta Sebaran Kos Putri SCBD",
    page_icon="🗺️",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/kost_putri_cleaned.csv")
    except Exception:
        df = pd.read_csv("../data/kost_putri_cleaned.csv")
        
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

df = load_data()

st.title("🗺️ Peta Interaktif Sebaran Kos Putri SCBD")
st.caption("Eksplorasi visual titik kos di sekitar kampus UPN Veteran, STIE YKPN, dan Atma Jaya Babarsari.")

# Sidebar Filters
st.sidebar.header("🔍 Filter Tampilan Peta")
filter_ac = st.sidebar.checkbox("❄️ Hanya yang ada AC")
filter_km = st.sidebar.checkbox("🚿 Hanya yang ada KM Dalam")
filter_wifi = st.sidebar.checkbox("📶 Hanya yang ada Wi-Fi")

kategori_harga = st.sidebar.multiselect(
    "Kategori Rentang Biaya",
    options=["< Rp800.000 (Hijau)", "Rp800.000 - Rp1.200.000 (Kuning)", "> Rp1.200.000 (Merah)", "Tanya Pemilik (Abu-abu)"],
    default=["< Rp800.000 (Hijau)", "Rp800.000 - Rp1.200.000 (Kuning)", "> Rp1.200.000 (Merah)", "Tanya Pemilik (Abu-abu)"]
)

# Filter logic
color_map_selection = {
    "< Rp800.000 (Hijau)": "green",
    "Rp800.000 - Rp1.200.000 (Kuning)": "orange",
    "> Rp1.200.000 (Merah)": "red",
    "Tanya Pemilik (Abu-abu)": "gray"
}
selected_colors = [color_map_selection[k] for k in kategori_harga]

filtered_df = df[df['marker_color'].isin(selected_colors)]
if filter_ac: filtered_df = filtered_df[filtered_df['has_ac'] == True]
if filter_km: filtered_df = filtered_df[filtered_df['has_km_dalam'] == True]
if filter_wifi: filtered_df = filtered_df[filtered_df['has_wifi'] == True]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Kos Ditampilkan", f"{len(filtered_df)} Titik")
col2.metric("🟢 < 800rb", f"{len(filtered_df[filtered_df['marker_color'] == 'green'])}")
col3.metric("🟡 800rb - 1.2jt", f"{len(filtered_df[filtered_df['marker_color'] == 'orange'])}")
col4.metric("🔴 > 1.2jt", f"{len(filtered_df[filtered_df['marker_color'] == 'red'])}")

# Build Folium Map
m = folium.Map(location=[-7.7720, 110.4080], zoom_start=14, tiles="CartoDB positron")

# Campus Landmarks
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

# Kos Markers
for _, row in filtered_df.iterrows():
    harga_label = f"Rp {int(row['harga_min']):,} / bln".replace(",", ".") if pd.notna(row['harga_min']) else "Tanya Pemilik"
    
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
        <p style='margin:0; font-weight:bold; color:#0f766e;'>💰 {harga_label}</p>
        <p style='margin:4px 0; font-size:11px;'><b>📍</b> {row['Alamat'][:50]}...</p>
        <p style='margin:4px 0; font-size:11px;'><b>✨</b> {fac_badges}</p>
        {wa_btn}
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"{row['Nama Kos']} ({harga_label})",
        icon=folium.Icon(color=row['marker_color'], icon="home")
    ).add_to(m)

# Render Folium in Streamlit
map_html = m._repr_html_()
html(map_html, height=600)
