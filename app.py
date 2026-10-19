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

MODEL_PATH = Path(__file__).parent / "ml" / "hasil" / "model_klasifikasi.joblib"


# ============================================================
# GAYA TAMPILAN
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4faff 0%, #ffffff 48%, #f5fbff 100%);
    }
    .block-container {
        padding-top: 1.7rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 22px;
        background: linear-gradient(120deg, #073b5c 0%, #087e9c 58%, #38a6b5 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        color: white;
        margin-bottom: .45rem;
        font-size: 2.15rem;
    }
    .hero p {
        color: #e8f8ff;
        font-size: 1rem;
        margin-bottom: 0;
    }
    .info-card {
        border: 1px solid #dceaf2;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        background: #ffffff;
        min-height: 125px;
    }
    .info-card h3 {
        color: #075985;
        font-size: 1rem;
        margin-bottom: .35rem;
    }
    .info-card p {
        color: #334155;
        font-size: .92rem;
        margin-bottom: 0;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dceaf2;
        padding: 1rem;
        border-radius: 15px;
    }
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: #087e9c;
        border-color: #087e9c;
        border-radius: 10px;
        font-weight: 600;
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
        "File model belum ditemukan. Pastikan file "
        "`ml/hasil/model_klasifikasi.joblib` sudah ada di repository GitHub."
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
# NAVIGASI
# ============================================================
with st.sidebar:
    st.markdown("## 🌊 Gelombang Laut")
    st.caption("Aplikasi klasifikasi berbasis Machine Learning")
    halaman = st.radio(
        "Menu navigasi",
        ["Beranda", "Prediksi", "Informasi Model", "Evaluasi Model"],
        label_visibility="visible",
    )
    st.divider()
    st.caption("Model: Decision Tree")
    st.caption("Kategori target: Tenang dan Rendah")


# ============================================================
# BERANDA
# ============================================================
if halaman == "Beranda":
    st.markdown(
        """
        <div class="hero">
            <h1>🌊 Klasifikasi Kondisi Gelombang Laut</h1>
            <p>
                Kenali kategori gelombang laut berdasarkan data lokasi,
                cuaca, kondisi arus, dan aktivitas gempa.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "Aplikasi ini menggunakan model **Decision Tree** yang telah dilatih "
        "melalui notebook `ml/model_klasifikasi.ipynb`. Pengguna dapat memasukkan "
        "nilai sejumlah variabel, kemudian model memperkirakan kategori gelombang "
        "menjadi **Tenang** atau **Rendah**."
    )

    akurasi = bundle.get("test_accuracy")
    cv_mean = bundle.get("cv_mean_accuracy")
    jumlah_fitur = len(features)

    c1, c2, c3 = st.columns(3)
    c1.metric("Algoritma", "Decision Tree")
    c2.metric("Fitur model", jumlah_fitur)
    c3.metric(
        "Akurasi data testing",
        f"{akurasi * 100:.2f}%" if akurasi is not None else "Tidak tersedia",
    )

    st.markdown("### Apa yang bisa dilakukan di aplikasi ini?")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="info-card">
                <h3>🧭 Prediksi kategori</h3>
                <p>Masukkan data lokasi, cuaca, arus laut, dan aktivitas gempa
                untuk memperoleh hasil klasifikasi dari model.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            """
            <div class="info-card">
                <h3>🌬️ Faktor yang digunakan</h3>
                <p>Model menggunakan 10 fitur input. Tinggi gelombang tidak
                dimasukkan sebagai input karena tidak digunakan sebagai fitur model.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="info-card">
                <h3>📊 Informasi model</h3>
                <p>Lihat algoritma, jumlah fitur, akurasi pengujian, dan
                kontribusi relatif fitur apabila informasinya tersedia.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            """
            <div class="info-card">
                <h3>⚠️ Batasan penggunaan</h3>
                <p>Hasil merupakan prediksi dari input pengguna, bukan pengukuran
                gelombang aktual atau informasi cuaca real-time.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "Mulai dari menu **Prediksi** di sidebar untuk mencoba model dengan "
        "nilai yang ingin dianalisis."
    )
    if cv_mean is not None:
        st.caption(
            f"Rata-rata akurasi 5-fold cross-validation dari notebook: {cv_mean * 100:.2f}%."
        )


# ============================================================
# PREDIKSI
# ============================================================
elif halaman == "Prediksi":
    st.title("🔎 Prediksi Kategori Gelombang")
    st.write(
        "Masukkan nilai fitur sesuai satuan dan rentang yang digunakan pada dataset penelitian. "
        "Nilai awal di bawah hanya contoh input dan dapat diubah."
    )

    with st.form("prediction_form"):
        st.markdown("#### 1. Lokasi perairan")
        loc1, loc2 = st.columns(2)
        with loc1:
            latitude = st.number_input(
                "Latitude", min_value=-90.0, max_value=90.0,
                value=-3.99, step=0.01, format="%.6f"
            )
        with loc2:
            longitude = st.number_input(
                "Longitude", min_value=-180.0, max_value=180.0,
                value=122.51, step=0.01, format="%.6f"
            )

        st.markdown("#### 2. Kondisi cuaca")
        cuaca1, cuaca2 = st.columns(2)
        with cuaca1:
            temperature = st.number_input(
                "Suhu (temperature)", value=28.0, step=0.5, format="%.2f"
            )
            wind_speed = st.number_input(
                "Kecepatan angin (wind_speed)", min_value=0.0,
                value=5.0, step=0.5, format="%.2f"
            )
        with cuaca2:
            humidity = st.number_input(
                "Kelembapan (humidity, %)", min_value=0.0, max_value=100.0,
                value=80.0, step=1.0, format="%.2f"
            )
            wind_gust = st.number_input(
                "Hembusan angin (wind_gust)", min_value=0.0,
                value=7.0, step=0.5, format="%.2f"
            )

        st.markdown("#### 3. Kondisi arus laut")
        current_speed = st.number_input(
            "Kecepatan arus (current_speed)", min_value=0.0,
            value=0.5, step=0.1, format="%.2f"
        )

        st.markdown("#### 4. Aktivitas gempa dalam 24 jam")
        gempa1, gempa2 = st.columns(2)
        with gempa1:
            jumlah_gempa = st.number_input(
                "Jumlah gempa (jumlah_gempa_24jam)",
                min_value=0, value=0, step=1
            )
            magnitude = st.number_input(
                "Magnitudo maksimum (magnitude_maks_24jam)",
                min_value=0.0, value=0.0, step=0.1, format="%.2f"
            )
        with gempa2:
            jarak_gempa = st.number_input(
                "Jarak gempa terdekat (km)",
                min_value=0.0, value=9999.0, step=10.0, format="%.2f",
                help=(
                    "Dalam dataset penelitian, 9999 digunakan sebagai penanda "
                    "ketika tidak ada gempa yang memenuhi kondisi pencarian. "
                    "Gunakan nilai ini hanya jika sesuai dengan pengolahan dataset."
                ),
            )
            st.caption(
                "Pastikan cara pengisian aktivitas gempa konsisten dengan dataset penelitian."
            )

        st.info(
            "Tinggi gelombang (wave_height) tidak diminta karena tidak digunakan "
            "sebagai fitur model, untuk menghindari target leakage."
        )
        submitted = st.form_submit_button(
            "🌊 Prediksi kategori gelombang", type="primary", use_container_width=True
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

        input_df = pd.DataFrame(
            [[input_values[name] for name in features]],
            columns=features,
        )
        prediction = model.predict(input_df)[0]

        st.divider()
        st.subheader("Hasil klasifikasi")
        if str(prediction).lower() == "tenang":
            st.success(f"### 🌤️ Kategori gelombang diprediksi: {prediction}")
            st.write(
                "Berdasarkan pola yang dipelajari model, data input ini "
                "diklasifikasikan ke kategori Tenang."
            )
        else:
            st.warning(f"### 🌊 Kategori gelombang diprediksi: {prediction}")
            st.write(
                "Berdasarkan pola yang dipelajari model, data input ini "
                "diklasifikasikan ke kategori Rendah."
            )

        st.caption(
            "Interpretasi di atas menjelaskan label model, bukan konfirmasi "
            "kondisi laut aktual. Periksa sumber resmi sebelum mengambil keputusan keselamatan."
        )

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_df)[0]
            probability_df = pd.DataFrame(
                {
                    "Kategori": classes,
                    "Probabilitas model": probabilities,
                }
            ).sort_values("Probabilitas model", ascending=False)
            st.markdown("#### Probabilitas keluaran model")
            st.bar_chart(probability_df.set_index("Kategori"))
            st.caption(
                "Probabilitas adalah keluaran internal model dan bukan jaminan "
                "kepastian kondisi gelombang."
            )

        with st.expander("Lihat kembali data input"):
            st.dataframe(
                pd.DataFrame(
                    {"Fitur": features, "Nilai input": [input_values[name] for name in features]}
                ),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# INFORMASI MODEL
# ============================================================
elif halaman == "Informasi Model":
    st.title("🧠 Informasi Model")
    st.write(
        "Informasi berikut merangkum model klasifikasi yang disimpan dari notebook "
        "`ml/model_klasifikasi.ipynb`."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Algoritma", "Decision Tree")
    c2.metric("Jumlah fitur", len(features))
    acc = bundle.get("test_accuracy")
    c3.metric(
        "Akurasi testing",
        f"{acc * 100:.2f}%" if acc is not None else "Tidak tersedia",
    )

    st.markdown("### Fitur yang digunakan")
    feature_groups = {
        "Lokasi": ["latitude", "longitude"],
        "Cuaca": ["temperature", "humidity", "wind_speed", "wind_gust"],
        "Kondisi laut": ["current_speed"],
        "Aktivitas gempa": [
            "jumlah_gempa_24jam",
            "magnitude_maks_24jam",
            "jarak_gempa_terdekat_km",
        ],
    }
    for group_name, group_features in feature_groups.items():
        with st.expander(group_name, expanded=True):
            for feature in group_features:
                if feature in features:
                    st.markdown(f"- `{feature}`")

    st.markdown("### Cara kerja singkat")
    st.markdown(
        """
        1. Pengguna memasukkan nilai dari 10 fitur.
        2. Aplikasi menyusun input sesuai urutan fitur yang tersimpan bersama model.
        3. Model Decision Tree menghasilkan prediksi kategori.
        4. Jika tersedia, aplikasi juga menampilkan probabilitas keluaran model.
        """
    )

    st.warning(
        "Model tidak mengambil data cuaca, arus, atau gempa secara real-time. "
        "Prediksi hanya berdasarkan nilai yang dimasukkan pengguna."
    )


# ============================================================
# EVALUASI MODEL
# ============================================================
elif halaman == "Evaluasi Model":
    st.title("📊 Evaluasi Model")
    st.write(
        "Bagian ini menampilkan metrik evaluasi yang ikut disimpan dari notebook. "
        "Metrik yang tidak tersedia dalam file model tidak dibuat atau diperkirakan."
    )

    acc = bundle.get("test_accuracy")
    cv_mean = bundle.get("cv_mean_accuracy")
    cv_std = bundle.get("cv_std_accuracy")

    e1, e2, e3 = st.columns(3)
    e1.metric(
        "Akurasi data testing",
        f"{acc * 100:.2f}%" if acc is not None else "Tidak tersedia",
    )
    e2.metric(
        "Rata-rata 5-fold CV",
        f"{cv_mean * 100:.2f}%" if cv_mean is not None else "Tidak tersedia",
    )
    e3.metric(
        "Standar deviasi CV",
        f"{cv_std:.4f}" if cv_std is not None else "Tidak tersedia",
    )

    st.markdown("### Bagaimana membaca metrik?")
    st.markdown(
        """
        - **Akurasi testing** menunjukkan proporsi prediksi yang sesuai dengan label
          aktual pada data testing.
        - **Rata-rata 5-fold cross-validation** merangkum akurasi dari lima pembagian
          data selama validasi silang.
        - **Standar deviasi CV** menggambarkan variasi skor antar-fold; nilainya perlu
          dilihat bersama rata-rata CV.
        """
    )

    importance = bundle.get("feature_importance")
    if importance:
        st.markdown("### Kontribusi relatif fitur")
        importance_df = pd.DataFrame(importance)
        if {"feature", "importance"}.issubset(importance_df.columns):
            importance_df = importance_df.sort_values("importance", ascending=True)
            st.bar_chart(importance_df.set_index("feature"))
            st.caption(
                "Feature importance menunjukkan kontribusi relatif fitur dalam "
                "pembentukan pohon, bukan hubungan sebab-akibat."
            )
    else:
        st.info("Informasi feature importance tidak ditemukan di file model.")

    st.caption(
        "Confusion matrix dan classification report tidak ditampilkan karena "
        "keduanya tidak disimpan dalam bundle model yang digunakan aplikasi ini."
    )


# ============================================================
# CATATAN DI SELURUH APLIKASI
# ============================================================
st.divider()
st.caption(
    "Aplikasi untuk eksplorasi hasil model klasifikasi. Hasil bukan data real-time "
    "dan tidak menggantikan informasi resmi keselamatan pelayaran."
)
