import streamlit as st
import pandas as pd
import base64
import os

# ==== FUNGSI SET BACKGROUND BLUR ====
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        backdrop-filter: blur(6px);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# === WRAPPER BOX BURAM ===
st.markdown(
    """
    <style>
    .blur-box {
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(1px);
        border-radius: 12px;
        padding: 20px;
        margin: auto;
        max-width: 900px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==== LOAD & CLEAN DATA ====
@st.cache_data
def load_data(csv_path):
    try:
        df = pd.read_csv(csv_path, sep=";", engine="python")
        df.columns = df.columns.str.strip()

        # Buat kolom duplikat menjadi unik
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            dup_idxs = cols[cols == dup].index.tolist()
            for i, idx in enumerate(dup_idxs):
                if i != 0:
                    cols[idx] = f"{dup}_{i+1}"
        df.columns = cols
        df.fillna("-", inplace=True)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

# ==== KONFIGURASI FILE (semua di folder yang sama) ====
CSV_FILE = "data SMKN1LAMBU_new update.csv"
LOGO_IMAGE = "logo.jpg"
BACKGROUND_IMAGE = "background.jpg"

# ==== SET BACKGROUND ====
if os.path.exists(BACKGROUND_IMAGE):
    set_background(BACKGROUND_IMAGE)

# ==== HEADER TAMPAK ATAS ====
if os.path.exists(LOGO_IMAGE):
    with open(LOGO_IMAGE, "rb") as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode()
else:
    logo_base64 = ""

st.markdown(
    f"""
    <div style='text-align: center; padding: 20px; background-color: rgba(255,255,255,0.8); border-radius: 12px; margin-bottom: 20px;'>
        <h2 style='color: #003366;'> WEBSITE PENCARIAN DATA SISWA</h2>
        <img src='data:image/png;base64,{logo_base64}' width='120'/>
        <h3 style='font-weight: bold; margin-top: 10px;'>SMK NEGERI 1 LAMBU</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# ==== MUAT DATA ====
data = load_data(CSV_FILE)
if data.empty:
    st.stop()

# ==== IDENTIFIKASI KOLOM UTAMA ====
col_nama = next((c for c in data.columns if "nama" in c.lower()), None)
col_nisn = next((c for c in data.columns if "nisn" in c.lower()), None)
col_rombel = next((c for c in data.columns if "rombel" in c.lower()), None)
col_jurusan = next((c for c in data.columns if "jurusan" in c.lower()), None)

# === VALIDASI KOLOM ===
missing = []
if not col_nama:
    missing.append("Nama")
if not col_nisn:
    missing.append("NISN")
if not col_rombel:
    missing.append("Rombel")
if not col_jurusan:
    missing.append("Jurusan")

if missing:
    st.error(f"Kolom berikut tidak ditemukan: {', '.join(missing)}")
    st.stop()

# === FORM PENCARIAN ===
with st.container():
    st.markdown("### 🔎 Tempat Pencarian Data")
    search_by = st.selectbox("Cari berdasarkan:", ["Nama", "NISN", "Rombel", "Jurusan"])
    search_input = st.text_input(f"Masukkan {search_by}")

    if st.button("Cari"):
        if not search_input.strip():
            st.warning("Silakan masukkan kata kunci pencarian.")
        else:
            hasil = pd.DataFrame()
            key = search_input.strip().upper()

            if search_by == "Nama":
                hasil = data[data[col_nama].astype(str).str.contains(search_input, case=False, na=False)]
            elif search_by == "NISN":
                hasil = data[data[col_nisn].astype(str).str.contains(search_input, case=False, na=False)]
            elif search_by == "Rombel":
                rombel_series = data[col_rombel].astype(str).str.upper().str.strip()
                if key in ["X", "XI", "XII"]:
                    hasil = data[rombel_series.str.startswith(key + " ")]
                else:
                    hasil = data[rombel_series.str.contains(search_input, case=False, na=False)]
            elif search_by == "Jurusan":
                hasil = data[data[col_jurusan].astype(str).str.contains(search_input, case=False, na=False)]

            if not hasil.empty:
                st.success(f"✅ Ditemukan {len(hasil)} data siswa:")
                st.dataframe(hasil)

                # === Download sebagai CSV ===
                csv_buf = hasil.to_csv(index=False).encode()
                b64_csv = base64.b64encode(csv_buf).decode()
                download_link_csv = f'<a href="data:file/csv;base64,{b64_csv}" download="hasil_pencarian.csv">📄 Download Hasil sebagai CSV</a>'
                st.markdown(download_link_csv, unsafe_allow_html=True)
            else:
                st.error("❌ Data tidak ditemukan.")

# === TAMPILKAN SELURUH DATA ===
with st.expander("📋 Tampilkan Seluruh Data Siswa"):
    st.dataframe(data)

# === SIDEBAR INFO ===
st.sidebar.header("🧾 Kolom Tersedia")
st.sidebar.write(data.columns.tolist())
