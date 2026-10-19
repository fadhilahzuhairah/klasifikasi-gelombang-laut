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
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">MODEL PERFORMANCE</div>
            <h1>Evaluasi Model</h1>
            <p>
                Lihat ringkasan performa model Decision Tree berdasarkan
                metrik evaluasi yang tersimpan dari proses pelatihan.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    acc = bundle.get("test_accuracy")
    cv_mean = bundle.get("cv_mean_accuracy")
    cv_std = bundle.get("cv_std_accuracy")

    st.markdown("### Ringkasan performa model")

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

    st.markdown("### Memahami hasil evaluasi")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Akurasi data testing")
        st.write(
            "Menunjukkan proporsi prediksi yang sesuai dengan label "
            "aktual pada data pengujian."
        )

        st.markdown("#### Rata-rata 5-Fold Cross-Validation")
        st.write(
            "Merangkum rata-rata skor akurasi dari lima pembagian "
            "data selama proses validasi silang."
        )

    with col2:
        st.markdown("#### Standar deviasi CV")
        st.write(
            "Menggambarkan variasi skor antar-fold. Nilainya perlu "
            "dibaca bersama rata-rata cross-validation."
        )

        st.markdown("#### Catatan evaluasi")
        st.write(
            "Nilai metrik ditampilkan sesuai informasi yang tersimpan "
            "di dalam bundle model."
        )

    importance = bundle.get("feature_importance")

    if importance:
        st.divider()
        st.markdown("### Kontribusi relatif fitur")

        importance_df = pd.DataFrame(importance)

        if {"feature", "importance"}.issubset(importance_df.columns):
            importance_df = importance_df.sort_values(
                "importance", ascending=True
            )

            st.bar_chart(importance_df.set_index("feature"))

            st.caption(
                "Feature importance menunjukkan kontribusi relatif fitur "
                "dalam pembentukan pohon, bukan hubungan sebab-akibat."
            )
    else:
        st.info(
            "Informasi feature importance tidak ditemukan "
            "di dalam file model."
        )

    st.caption(
        "Confusion matrix dan classification report tidak ditampilkan "
        "karena keduanya tidak disimpan dalam bundle model yang digunakan."
    )

# ============================================================
# CATATAN DI SELURUH APLIKASI
# ============================================================
st.divider()
st.caption(
    "Aplikasi untuk eksplorasi hasil model klasifikasi. Hasil bukan data real-time "
    "dan tidak menggantikan informasi resmi keselamatan pelayaran."
)
