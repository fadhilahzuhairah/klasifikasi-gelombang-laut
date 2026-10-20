# Streamlit - Klasifikasi Kondisi Gelombang Laut

## File yang disiapkan
- `app.py`: aplikasi Streamlit dengan input 10 fitur yang dipakai model.
- `requirements.txt`: pustaka untuk deploy.
- `ml/model_klasifikasi.ipynb`: salinan notebook dengan satu cell tambahan di akhir untuk menyimpan model.

## Cara menambahkan ke repository
1. Salin `app.py` ke folder utama repository.
2. Perbarui `requirements.txt` dengan isi dari paket ini. Jika requirements lama berisi dependensi Airflow atau MySQL yang masih dipakai project lain, jangan hapus baris tersebut; cukup tambahkan `streamlit` dan `joblib`.
3. Gunakan cell penyimpanan model di akhir notebook yang sudah diperbarui. Sebaiknya salin cell tersebut ke notebook asli di repository agar perubahan notebook lain tidak tertimpa.
4. Jalankan notebook sampai pelatihan dan evaluasi selesai, lalu jalankan cell terakhir. Cell ini memerlukan variabel `model`, `fitur`, `accuracy`, `cv_scores`, dan `feature_importance` yang sudah dibuat oleh cell sebelumnya.
5. Pastikan file `ml/hasil/model_klasifikasi.joblib` berhasil dibuat dan unggah ke GitHub. Jangan unggah data rahasia atau kredensial database.
6. Di Streamlit Community Cloud, pilih repository dan branch `main`, lalu set **Main file path** ke `app.py`.

## Penting
- Aplikasi tidak terhubung ke MySQL saat runtime. Notebook tetap menggunakan MySQL saat mengumpulkan dan melatih data.
- File model `.joblib` belum disertakan karena harus dibuat dari model yang benar-benar dilatih di lingkungan penelitianmu.
- Jika dataset pelatihan berubah, jalankan ulang notebook dan buat ulang file model.
- Pastikan kamu hanya menggabungkan perubahan yang dibutuhkan ke `requirements.txt` repository yang sudah ada.
