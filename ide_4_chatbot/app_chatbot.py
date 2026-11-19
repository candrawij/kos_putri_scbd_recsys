import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(
    page_title="AI Chatbot Asisten Kos Putri SCBD",
    page_icon="🤖",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        return pd.read_csv("data/kost_putri_cleaned.csv")
    except Exception:
        return pd.read_csv("../data/kost_putri_cleaned.csv")

df = load_data()

st.title("🤖 Chatbot Asisten Pencari Kos Putri SCBD")
st.caption("Tanyakan kriteria kos impian Anda dengan bahasa sehari-hari. Asisten pintar akan mencarikan pilihan yang paling cocok dari direktori.")

# ----------------- ENGINE CHATBOT -----------------
def parse_user_query(query_text):
    text = query_text.lower()
    criteria = {'max_budget': None, 'facilities': {}, 'location': None}
    
    # 1. Budget
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
            if raw_nums:
                criteria['max_budget'] = int(raw_nums[0])

    # 2. Fasilitas
    if re.search(r'\bac\b|air conditioner', text): criteria['facilities']['has_ac'] = True
    if re.search(r'km dalam|kamar mandi dalam|kamar mandi', text): criteria['facilities']['has_km_dalam'] = True
    if re.search(r'wifi|wi-fi|internet', text): criteria['facilities']['has_wifi'] = True
    if re.search(r'listrik', text): criteria['facilities']['has_listrik'] = True

    # 3. Lokasi
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
        if required:
            candidate_df = candidate_df[candidate_df[fac_col] == True]
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

# ----------------- CHAT INTERFACE -----------------
# Inisialisasi riwayat obrolan
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

# Render riwayat pesan
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Tangani input pesan baru dari pengguna
if prompt := st.chat_input("Tulis pertanyaan pencarian kos di sini..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Proses balasan asisten
    response = generate_bot_response(prompt, df)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
