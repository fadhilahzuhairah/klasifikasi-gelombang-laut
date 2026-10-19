
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Klasifikasi Gelombang Laut",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_PATH = (
    Path(__file__).parent
    / "ml"
    / "hasil"
    / "model_klasifikasi.joblib"
)


# ============================================================
# CSS DASHBOARD MODERN
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #f3f8fc;
        color: #183650;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stHeader"] {
        background: rgba(243, 248, 252, 0.92);
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102c49, #173c60 75%, #102c49);
        border-right: 1px solid #244b6c;
    }

    section[data-testid="stSidebar"] * {
        color: #e8f3ff;
    }

    .brand {
        font-size: 1.18rem;
        font-weight: 800;
        line-height: 1.4;
        color: #ffffff;
        margin: 0.5rem 0;
    }

    .brand-sub {
        color: #a8c9e8;
        font-size: 0.82rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .sidebar-note {
        color: #c1d7eb;
        font-size: 0.82rem;
        line-height: 1.7;
        margin-top: 1rem;
    }

    /* MENU BERBENTUK TOMBOL, BUKAN RADIO */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        min-height: 45px;
        text-align: left;
        border-radius: 9px;
        padding: 0.55rem 0.8rem;
        margin: 3px 0;
        font-size: 0.91rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: #2879b9;
        color: #ffffff;
        border: 1px solid #4694d0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }

    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: transparent;
        color: #e8f3ff;
        border: 1px solid transparent;
    }

    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background: rgba(104, 177, 235, 0.17);
        border-color: rgba(156, 205, 244, 0.3);
        color: #ffffff;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(218, 236, 255, 0.2);
    }

    /* HERO */
    .hero {
        border: 1px solid #d8eaf7;
        border-radius: 17px;
        padding: 1.7rem 1.8rem;
        margin-bottom: 1rem;
        background:
            linear-gradient(
                90deg,
                rgba(245, 251, 255, .98) 0%,
                rgba(245, 251, 255, .92) 55%,
                rgba(229, 244, 253, .55) 100%
            ),
            url("https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1800&q=85");
        background-size: cover;
        background-position: center;
        box-shadow: 0 5px 20px rgba(29, 79, 119, 0.05);
    }

    .hero-eyebrow {
        color: #087ca5;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        margin-bottom: 0.5rem;
    }

    .hero h1 {
        color: #153b5c;
        font-size: clamp(1.65rem, 2.5vw, 2.3rem);
        line-height: 1.25;
        font-weight: 800;
        margin: 0 0 0.7rem;
    }

    .hero p {
        max-width: 760px;
        color: #34536e;
        font-size: 0.95rem;
        line-height: 1.7;
        margin: 0;
    }

    .section-title {
        color: #183c5b;
        font-size: 1.28rem;
        font-weight: 800;
        margin: 0.5rem 0 0.2rem;
    }

    .section-subtitle {
        color: #647e95;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .summary-wrap {
        background: #ffffff;
        border: 1px solid #dceaf4;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.7rem 0 1.25rem;
    }

    div[data-testid="stMetric"] {
        background: #f8fbfe;
        border: 1px solid #e2edf5;
        border-radius: 11px;
        padding: 0.9rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #5e7890;
        font-size: 0.82rem;
    }

    div[data-testid="stMetricValue"] {
        color: #174e7c;
        font-size: 1.4rem;
        font-weight: 800;
    }

    /* KARTU BERANDA */
    .info-card {
        min-height: 145px;
        background: #ffffff;
        border: 1px solid #dceaf4;
        border-radius: 13px;
        padding: 1.15rem;
        margin-bottom: 0.8rem;
    }

    .info-card h3 {
        color: #174e7c;
        font-size: 1.05rem;
        margin: 0 0 0.55rem;
    }

    .info-card p {
        color: #526c82;
        font-size: 0.9rem;
        line-height: 1.65;
        margin: 0;
    }

    /* FORM */
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #dce8f1;
        border-radius: 15px;
        padding: 1rem;
    }

    .input-title {
        font-size: 0.95rem;
        font-weight: 800;
        padding: 0.8rem;
        border-radius: 9px;
        margin: 0.3rem 0 0.7rem;
    }

    .loc-title {
        color: #1c5c9a;
        background: #e5f1ff;
        border: 1px solid #d3e6fc;
    }

    .weather-title {
        color: #79582b;
        background: #fff4df;
        border: 1px solid #f3e3c2;
    }

    .current-title {
        color: #126a73;
        background: #e1f6f4;
        border: 1px solid #ccebe8;
    }

    .quake-title {
        color: #394a9b;
        background: #eeefff;
        border: 1px solid #dfe1fb;
    }

    .notice {
        padding: 0.85rem 1rem;
        border-radius: 9px;
        background: #eaf5ff;
        border: 1px solid #d5eaff;
        color: #2a6597;
        font-size: 0.88rem;
        line-height: 1.6;
        margin: 0.8rem 0;
    }

    div.stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(100deg, #1762a2, #174d83);
        border: 1px solid #174d83;
        color: white;
        border-radius: 9px;
        min-height: 2.9rem;
        font-weight: 700;
    }

    div.stFormSubmitButton > button[kind="primary"]:hover {
        background: #0d426f;
        border-color: #0d426f;
    }

    @media (max-width: 900px) {
        .hero {
            padding: 1.25rem;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MEMUAT MODEL
# ============================================================
@st.cache_resource
def load_model_bundle(path):
    return joblib.load(path)


if not MODEL_PATH.exists():
    st.error(
        "File model tidak ditemukan. Pastikan file "
        "`ml/hasil/model_klasifikasi.joblib` tersedia di GitHub."
    )
    st.stop()

try:
    bundle = load_model_bundle(str(MODEL_PATH))
    model = bundle["model"]
    features = bundle["features"]
    classes = list(bundle.get("classes", model.classes_))
except Exception as exc:
    st.error(f"Model gagal dimuat: {exc}")
    st.stop()


# ============================================================
# FUNGSI RINGKASAN MODEL
# ============================================================
def show_model_summary():
    accuracy = bundle.get("test_accuracy")

    col1, col2, col3 = st.columns(3)

    col1.metric("Algoritma", "Decision Tree")
    col2.metric("Jumlah fitur", f"{len(features)} fitur")
    col3.metric(
        "Akurasi data testing",
        f"{accuracy * 100:.2f}%" if accuracy is not None else "Tidak tersedia",
    )


def show_feature_importance():
    importance = bundle.get("feature_importance")

    if importance:
        importance_df = pd.DataFrame(importance)

        if {"feature", "importance"}.issubset(importance_df.columns):
            importance_df = importance_df.sort_values(
                "importance", ascending=True
            )

            st.markdown("### Kontribusi Relatif Fitur")
            st.bar_chart(importance_df.set_index("feature"))

            st.caption(
                "Feature importance menunjukkan kontribusi relatif fitur "
                "dalam model, bukan hubungan sebab-akibat."
            )


# ============================================================
# SIDEBAR NAVIGATION - TOMBOL MODERN TANPA BULATAN
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">🌊 Klasifikasi<br>Gelombang Laut</div>
        <div class="brand-sub">
            Dashboard prediksi kondisi perairan
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        """
        <div style="
            color:#9fc5e8;
            font-size:0.75rem;
            font-weight:700;
            letter-spacing:1.5px;
            margin:10px 0 12px;">
            MENU NAVIGASI
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "halaman_aktif" not in st.session_state:
        st.session_state.halaman_aktif = "Beranda"

    menu = [
        ("⌂", "Beranda"),
        ("⌁", "Prediksi"),
        ("▤", "Informasi Model"),
        ("▥", "Evaluasi Model"),
    ]

    for ikon, nama in menu:
        aktif = st.session_state.halaman_aktif == nama

        if st.button(
            f"{ikon}     {nama}",
            key=f"menu_{nama}",
            use_container_width=True,
            type="primary" if aktif else "secondary",
        ):
            st.session_state.halaman_aktif = nama
            st.rerun()

    halaman = st.session_state.halaman_aktif

    st.divider()

    st.markdown(
        """
        <div class="sidebar-note">
            <b>MODEL</b><br>
            Decision Tree<br><br>
            <b>KATEGORI TARGET</b><br>
            Tenang dan Rendah
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BERANDA
# ============================================================
if halaman == "Beranda":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">MARINE CONDITION ANALYTICS</div>
            <h1>Prediksi Kategori Gelombang Laut</h1>
            <p>
                Analisis kategori gelombang laut berdasarkan data lokasi,
                cuaca, arus, dan aktivitas gempa menggunakan model
                Decision Tree yang telah dilatih.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="summary-wrap">', unsafe_allow_html=True)
    show_model_summary()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Jelajahi Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Gunakan menu di sebelah kiri untuk '
        'mengakses setiap fitur aplikasi.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="info-card">
                <h3>⌁ Prediksi Kategori</h3>
                <p>
                    Masukkan 10 fitur lokasi, cuaca, arus laut, dan aktivitas
                    gempa untuk mendapatkan hasil klasifikasi model.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <h3>⌖ Informasi Variabel</h3>
                <p>
                    Pelajari fitur yang digunakan model dan bagaimana data
                    input diproses sebelum menghasilkan prediksi.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="info-card">
                <h3>▥ Evaluasi Model</h3>
                <p>
                    Lihat ringkasan akurasi pengujian dan metrik lain
                    apabila tersedia dalam file model.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <h3>ⓘ Batasan Penggunaan</h3>
                <p>
                    Hasil merupakan prediksi model berdasarkan input,
                    bukan pengukuran laut aktual atau data real-time.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="notice">Penting: hasil prediksi tidak menggantikan '
        'informasi resmi keselamatan pelayaran.</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# PREDIKSI
# ============================================================
elif halaman == "Prediksi":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">PREDICTION WORKSPACE</div>
            <h1>Prediksi Kategori Gelombang Laut</h1>
            <p>
                Isi nilai parameter sesuai dataset penelitian. Nilai awal
                merupakan contoh input yang dapat kamu ubah.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="summary-wrap">', unsafe_allow_html=True)
    show_model_summary()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Masukkan Data</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Lengkapi nilai setiap kelompok fitur, '
        'kemudian jalankan prediksi.</div>',
        unsafe_allow_html=True,
    )

    with st.form("prediction_form"):
        loc, weather, current, quake = st.columns(4, gap="medium")

        with loc:
            st.markdown(
                '<div class="input-title loc-title">⌖ Lokasi</div>',
                unsafe_allow_html=True,
            )

            latitude = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=-3.99,
                step=0.01,
                format="%.6f",
            )

            longitude = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=122.51,
                step=0.01,
                format="%.6f",
            )

        with weather:
            st.markdown(
                '<div class="input-title weather-title">☼ Kondisi Cuaca</div>',
                unsafe_allow_html=True,
            )

            temperature = st.number_input(
                "Suhu (temperature)",
                value=28.0,
                step=0.5,
                format="%.2f",
            )

            humidity = st.number_input(
                "Kelembapan (%)",
                min_value=0.0,
                max_value=100.0,
                value=80.0,
                step=1.0,
                format="%.2f",
            )

        with current:
            st.markdown(
                '<div class="input-title current-title">≋ Angin dan Arus</div>',
                unsafe_allow_html=True,
            )

            wind_speed = st.number_input(
                "Kecepatan angin",
                min_value=0.0,
                value=5.0,
                step=0.5,
                format="%.2f",
            )

            wind_gust = st.number_input(
                "Hembusan angin",
                min_value=0.0,
                value=7.0,
                step=0.5,
                format="%.2f",
            )

            current_speed = st.number_input(
                "Kecepatan arus",
                min_value=0.0,
                value=0.5,
                step=0.1,
                format="%.2f",
            )

        with quake:
            st.markdown(
                '<div class="input-title quake-title">✣ Aktivitas Gempa</div>',
                unsafe_allow_html=True,
            )

            jumlah_gempa = st.number_input(
                "Jumlah gempa 24 jam",
                min_value=0,
                value=0,
                step=1,
            )

            magnitude = st.number_input(
                "Magnitudo maksimum",
                min_value=0.0,
                value=0.0,
                step=0.1,
                format="%.2f",
            )

            jarak_gempa = st.number_input(
                "Jarak gempa terdekat (km)",
                min_value=0.0,
                value=9999.0,
                step=10.0,
                format="%.2f",
                help=(
                    "Dalam dataset, 9999 digunakan sebagai penanda jika tidak "
                    "ada gempa yang memenuhi kondisi pencarian. Gunakan nilai "
                    "tersebut hanya jika sesuai dengan aturan dataset."
                ),
            )

        st.markdown(
            '<div class="notice">Tinggi gelombang tidak diminta sebagai input '
            'karena tidak digunakan sebagai fitur model.</div>',
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button(
            "🌊 Prediksi Kategori Gelombang",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        input_values = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_gust": wind_gust,
            "current_speed": current_speed,
            "jumlah_gempa_24jam": jumlah_gempa,
            "magnitude_maks_24jam": magnitude,
            "jarak_gempa_terdekat_km": jarak_gempa,
        }

        try:
            input_df = pd.DataFrame(
                [[input_values[name] for name in features]],
                columns=features,
            )
        except KeyError as exc:
            st.error(
                f"Fitur {exc} tidak ditemukan di form input. "
                "Periksa kesesuaian fitur model."
            )
            st.stop()

        prediction = model.predict(input_df)[0]

        st.divider()
        st.markdown(
            '<div class="section-title">Hasil Prediksi</div>',
            unsafe_allow_html=True,
        )

        if str(prediction).lower() == "tenang":
            st.success(f"Kategori gelombang diprediksi: **{prediction}**")
            st.write(
                "Berdasarkan pola yang dipelajari model, input ini "
                "diklasifikasikan ke kategori Tenang."
            )
        else:
            st.warning(f"Kategori gelombang diprediksi: **{prediction}**")
            st.write(
                "Berdasarkan pola yang dipelajari model, input ini "
                "diklasifikasikan ke kategori Rendah."
            )

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_df)[0]

            probability_df = pd.DataFrame(
                {
                    "Kategori": classes,
                    "Probabilitas model": probabilities,
                }
            ).sort_values("Probabilitas model", ascending=False)

            st.markdown("### Probabilitas Keluaran Model")
            st.bar_chart(probability_df.set_index("Kategori"))

            st.caption(
                "Probabilitas merupakan keluaran model, bukan jaminan "
                "kondisi gelombang aktual."
            )

        with st.expander("Lihat nilai input yang digunakan"):
            st.dataframe(
                pd.DataFrame(
                    {
                        "Fitur": features,
                        "Nilai input": [
                            input_values[name] for name in features
                        ],
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# INFORMASI MODEL
# ============================================================
elif halaman == "Informasi Model":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">MODEL OVERVIEW</div>
            <h1>Informasi Model</h1>
            <p>
                Ringkasan algoritma, fitur input, dan alur kerja model
                klasifikasi gelombang laut.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="summary-wrap">', unsafe_allow_html=True)
    show_model_summary()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Fitur yang Digunakan")

    feature_groups = {
        "Lokasi": ["latitude", "longitude"],
        "Cuaca": [
            "temperature",
            "humidity",
            "wind_speed",
            "wind_gust",
        ],
        "Kondisi arus laut": ["current_speed"],
        "Aktivitas gempa": [
            "jumlah_gempa_24jam",
            "magnitude_maks_24jam",
            "jarak_gempa_terdekat_km",
        ],
    }

    col1, col2 = st.columns(2)

    for index, (group_name, group_features) in enumerate(
        feature_groups.items()
    ):
        with col1 if index % 2 == 0 else col2:
            with st.expander(group_name, expanded=True):
                for feature in group_features:
                    if feature in features:
                        st.markdown(f"- `{feature}`")

    st.markdown("### Cara Kerja Prediksi")

    st.markdown(
        """
        1. Pengguna memasukkan nilai dari fitur yang dibutuhkan.
        2. Aplikasi menyusun data sesuai urutan fitur dalam model.
        3. Model Decision Tree memprediksi kategori gelombang.
        4. Aplikasi menampilkan hasil dan probabilitas jika tersedia.
        """
    )

    show_feature_importance()

    st.info(
        "Aplikasi ini tidak mengambil data cuaca atau gempa secara real-time. "
        "Prediksi bergantung pada nilai yang dimasukkan pengguna."
    )


# ============================================================
# EVALUASI MODEL
# ============================================================
elif halaman == "Evaluasi Model":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">MODEL PERFORMANCE</div>
            <h1>Evaluasi Model</h1>
            <p>
                Ringkasan performa model Decision Tree berdasarkan metrik
                evaluasi yang tersimpan dalam bundle model.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    acc = bundle.get("test_accuracy")
    cv_mean = bundle.get("cv_mean_accuracy")
    cv_std = bundle.get("cv_std_accuracy")

    e1, e2, e3 = st.columns(3)

    e1.metric(
        "Akurasi Data Testing",
        f"{acc * 100:.2f}%" if acc is not None else "Tidak tersedia",
    )

    e2.metric(
        "Rata-rata 5-Fold CV",
        f"{cv_mean * 100:.2f}%" if cv_mean is not None else "Tidak tersedia",
    )

    e3.metric(
        "Standar Deviasi CV",
        f"{cv_std:.4f}" if cv_std is not None else "Tidak tersedia",
    )

    st.divider()
    st.markdown("### Memahami Hasil Evaluasi")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Akurasi Data Testing")
        st.write(
            "Menunjukkan proporsi prediksi yang sesuai dengan label "
            "aktual pada data pengujian."
        )

        st.markdown("#### Rata-rata 5-Fold CV")
        st.write(
            "Merangkum rata-rata skor akurasi dari lima pembagian data "
            "selama validasi silang, jika tersedia."
        )

    with col2:
        st.markdown("#### Standar Deviasi CV")
        st.write(
            "Menggambarkan variasi skor antar-fold. Nilainya perlu "
            "dibaca bersama rata-rata cross-validation."
        )

        st.markdown("#### Catatan")
        st.write(
            "Nilai metrik hanya ditampilkan jika tersimpan di bundle model."
        )

    show_feature_importance()

    st.caption(
        "Confusion matrix dan classification report tidak ditampilkan "
        "karena tidak tersedia di bundle model yang digunakan."
    )


# ============================================================
# FOOTER
# ============================================================
st.divider()

st.caption(
    "Aplikasi klasifikasi berbasis model hasil pelatihan. Hasil bukan data "
    "real-time dan tidak menggantikan informasi resmi keselamatan pelayaran."
)
