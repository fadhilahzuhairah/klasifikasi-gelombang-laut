from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Klasifikasi Kondisi Gelombang Laut",
    page_icon="🌊",
    layout="wide",
)

st.title("🌊 Klasifikasi Kondisi Gelombang Laut")
st.write(
    "Aplikasi ini menggunakan model Decision Tree yang dilatih dari notebook "
    "`ml/model_klasifikasi.ipynb` untuk memprediksi kategori gelombang laut."
)

MODEL_PATH = Path(__file__).parent / "ml" / "hasil" / "model_klasifikasi.joblib"

@st.cache_resource
def load_model_bundle(path):
    return joblib.load(path)

if not MODEL_PATH.exists():
    st.error(
        "File model belum ditemukan. Jalankan ulang notebook "
        "`ml/model_klasifikasi.ipynb` setelah menambahkan cell penyimpanan model, "
        "lalu pastikan file `ml/hasil/model_klasifikasi.joblib` ikut diunggah ke GitHub."
    )
    st.stop()

bundle = load_model_bundle(MODEL_PATH)
model = bundle["model"]
features = bundle["features"]
classes = list(bundle.get("classes", model.classes_))

st.subheader("Informasi model")
m1, m2, m3 = st.columns(3)
m1.metric("Algoritma", "Decision Tree")
m2.metric("Jumlah fitur", len(features))
if bundle.get("test_accuracy") is not None:
    m3.metric("Akurasi data testing", f'{bundle["test_accuracy"] * 100:.2f}%')
else:
    m3.metric("Akurasi data testing", "Tidak tersedia")

st.caption(
    "Akurasi yang ditampilkan berasal dari evaluasi notebook, bukan jaminan "
    "bahwa setiap prediksi baru pasti benar."
)

st.divider()
st.subheader("Masukkan data untuk prediksi")
st.write(
    "Isi nilai yang tersedia untuk kondisi lokasi, cuaca, laut, dan gempa. "
    "Gunakan satuan yang sesuai dengan dataset penelitian."
)

with st.form("prediction_form"):
    left, middle, right = st.columns(3)

    with left:
        latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=-3.99, step=0.01, format="%.6f")
        longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=122.51, step=0.01, format="%.6f")
        temperature = st.number_input("Suhu (temperature)", value=28.0, step=0.5, format="%.2f")
        humidity = st.number_input("Kelembapan (humidity)", min_value=0.0, max_value=100.0, value=80.0, step=1.0, format="%.2f")

    with middle:
        wind_speed = st.number_input("Kecepatan angin (wind_speed)", min_value=0.0, value=5.0, step=0.5, format="%.2f")
        wind_gust = st.number_input("Hembusan angin (wind_gust)", min_value=0.0, value=7.0, step=0.5, format="%.2f")
        current_speed = st.number_input("Kecepatan arus (current_speed)", min_value=0.0, value=0.5, step=0.1, format="%.2f")
        jumlah_gempa = st.number_input("Jumlah gempa 24 jam", min_value=0, value=0, step=1)

    with right:
        magnitude = st.number_input("Magnitudo maksimum 24 jam", min_value=0.0, value=0.0, step=0.1, format="%.2f")
        jarak_gempa = st.number_input(
            "Jarak gempa terdekat (km)",
            min_value=0.0,
            value=9999.0,
            step=10.0,
            format="%.2f",
            help="Pada dataset penelitian, 9999 digunakan sebagai penanda ketika tidak ada gempa yang memenuhi kondisi pencarian. Gunakan penanda yang sama bila memang tidak ada gempa.",
        )
        st.info("Tinggi gelombang tidak diminta sebagai input karena tidak digunakan sebagai fitur model.")

    submitted = st.form_submit_button("Prediksi kategori gelombang", type="primary")

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
    input_df = pd.DataFrame([[input_values[name] for name in features]], columns=features)
    prediction = model.predict(input_df)[0]

    st.subheader("Hasil prediksi")
    if str(prediction).lower() == "tenang":
        st.success(f"Kategori gelombang diprediksi: **{prediction}**")
    else:
        st.warning(f"Kategori gelombang diprediksi: **{prediction}**")

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_df)[0]
        probability_df = pd.DataFrame({
            "Kategori": classes,
            "Probabilitas model": probabilities,
        }).sort_values("Probabilitas model", ascending=False)
        st.write("Probabilitas prediksi model")
        st.bar_chart(probability_df.set_index("Kategori"))
        st.caption(
            "Probabilitas ini merupakan keluaran model, bukan kepastian kondisi "
            "gelombang aktual."
        )

if bundle.get("feature_importance"):
    st.divider()
    st.subheader("Fitur yang berkontribusi pada model")
    importance_df = pd.DataFrame(bundle["feature_importance"])
    if not importance_df.empty and {"feature", "importance"}.issubset(importance_df.columns):
        importance_df = importance_df.sort_values("importance", ascending=True)
        st.bar_chart(importance_df.set_index("feature"))

st.divider()
st.caption(
    "Catatan: aplikasi ini menjalankan model hasil pelatihan. Prediksi tidak "
    "mengambil data cuaca atau gempa secara real-time dan bukan pengganti "
    "informasi resmi keselamatan pelayaran."
)
