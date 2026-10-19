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
