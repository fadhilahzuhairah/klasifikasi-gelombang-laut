# ============================================================
# IDENTITAS PROYEK
# ============================================================

NAMA_PROYEK = "Klasifikasi Kondisi Gelombang Laut"
NAMA_MAHASISWA = "Putri Fadhilah Zuhairah"
NIM = "ISI_NIM"
EMAIL = "ISI_EMAIL"


# ============================================================
# PERTANYAAN BISNIS
# ============================================================

business_questions = {

    "BQ1": """
    Bagaimana kondisi gelombang laut pada masing-masing wilayah
    perairan berdasarkan data cuaca dan kondisi laut?
    """,

    "BQ2": """
    Bagaimana hubungan antara kecepatan angin, tinggi gelombang,
    dan kecepatan arus terhadap kategori kondisi gelombang laut?
    """,

    "BQ3": """
    Bagaimana perbedaan kondisi gelombang laut berdasarkan lokasi
    wilayah perairan dan waktu pengamatan?
    """,

    "BQ4": """
    Dapatkah kondisi gelombang laut diklasifikasikan menjadi kategori
    Tenang dan Rendah berdasarkan faktor cuaca, kondisi laut, lokasi,
    waktu, dan aktivitas gempa?
    """
}


# ============================================================
# IMPORT LIBRARY
# ============================================================

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import mysql.connector

from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold
)

from sklearn.preprocessing import StandardScaler

from sklearn.pipeline import Pipeline

from sklearn.tree import (
    DecisionTreeClassifier,
    plot_tree
)

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# TAMPILAN AWAL
# ============================================================

print("\n" + "=" * 80)
print("PROYEK:", NAMA_PROYEK)
print("NAMA  :", NAMA_MAHASISWA)
print("NIM   :", NIM)
print("EMAIL :", EMAIL)
print("=" * 80)

print("\nPERTANYAAN BISNIS")
print("-" * 80)

for kode, pertanyaan in business_questions.items():
    print(f"\n{kode}: {pertanyaan.strip()}")


# ============================================================
# 1. GATHERING DATA DARI DATABASE MYSQL
# ============================================================

print("\n" + "=" * 80)
print("1. GATHERING DATA DARI DATABASE MYSQL")
print("=" * 80)

conn = mysql.connector.connect(
    host="host.docker.internal",
    user="root",
    password="root",
    database="airflow_db"
)


# ------------------------------------------------------------
# 1.1 DATA CUACA
# ------------------------------------------------------------

query_cuaca = """
SELECT *
FROM marine_data_cuaca
"""

df_cuaca = pd.read_sql(query_cuaca, conn)

print("\n[1] DATA CUACA")
print("Jumlah baris :", len(df_cuaca))
print("Jumlah kolom :", len(df_cuaca.columns))

print("\nKolom:")
print(df_cuaca.columns.tolist())

print("\nContoh data:")
print(df_cuaca.head())


# ------------------------------------------------------------
# 1.2 DATA KONDISI LAUT
# ------------------------------------------------------------

query_utama = """
SELECT *
FROM marine_data_utama
"""

df_utama = pd.read_sql(query_utama, conn)

print("\n[2] DATA KONDISI LAUT")
print("Jumlah baris :", len(df_utama))
print("Jumlah kolom :", len(df_utama.columns))

print("\nKolom:")
print(df_utama.columns.tolist())

print("\nContoh data:")
print(df_utama.head())


# ------------------------------------------------------------
# 1.3 DATA GEMPA
# ------------------------------------------------------------

query_gempa = """
SELECT *
FROM marine_data_gempa
"""

df_gempa = pd.read_sql(query_gempa, conn)

print("\n[3] DATA GEMPA")
print("Jumlah baris :", len(df_gempa))
print("Jumlah kolom :", len(df_gempa.columns))

print("\nKolom:")
print(df_gempa.columns.tolist())

print("\nContoh data:")
print(df_gempa.head())


conn.close()


# ============================================================
# 2. ASSESSING DATA SEBELUM CLEANING
# ============================================================

print("\n" + "=" * 80)
print("2. ASSESSING DATA SEBELUM CLEANING")
print("=" * 80)


# ------------------------------------------------------------
# 2.1 ASSESSING DATA CUACA
# ------------------------------------------------------------

print("\n" + "-" * 80)
print("ASSESSING DATA CUACA")
print("-" * 80)

print("\n--- INFO DATA ---")
df_cuaca.info()

print("\n--- STATISTIK DESKRIPTIF ---")
print(df_cuaca.describe(include="all"))

print("\n--- MISSING VALUES ---")
print(df_cuaca.isnull().sum())

print("\n--- JUMLAH DUPLIKAT ---")
print(df_cuaca.duplicated().sum())

print("\n--- 5 DATA PERTAMA ---")
print(df_cuaca.head())


# ------------------------------------------------------------
# 2.2 ASSESSING DATA KONDISI LAUT
# ------------------------------------------------------------

print("\n" + "-" * 80)
print("ASSESSING DATA KONDISI LAUT")
print("-" * 80)

print("\n--- INFO DATA ---")
df_utama.info()

print("\n--- STATISTIK DESKRIPTIF ---")
print(df_utama.describe(include="all"))

print("\n--- MISSING VALUES ---")
print(df_utama.isnull().sum())

print("\n--- JUMLAH DUPLIKAT ---")
print(df_utama.duplicated().sum())

print("\n--- 5 DATA PERTAMA ---")
print(df_utama.head())


# ------------------------------------------------------------
# 2.3 ASSESSING DATA GEMPA
# ------------------------------------------------------------

print("\n" + "-" * 80)
print("ASSESSING DATA GEMPA")
print("-" * 80)

print("\n--- INFO DATA ---")
df_gempa.info()

print("\n--- STATISTIK DESKRIPTIF ---")
print(df_gempa.describe(include="all"))

print("\n--- MISSING VALUES ---")
print(df_gempa.isnull().sum())

print("\n--- JUMLAH DUPLIKAT ---")
print(df_gempa.duplicated().sum())

print("\n--- 5 DATA PERTAMA ---")
print(df_gempa.head())


# ============================================================
# 3. CLEANING DATA SUMBER
# ============================================================

print("\n" + "=" * 80)
print("3. CLEANING DATA SUMBER")
print("=" * 80)


# ------------------------------------------------------------
# 3.1 CLEANING DATA CUACA
# ------------------------------------------------------------

print("\n[1] CLEANING DATA CUACA")

print("Data sebelum cleaning:", df_cuaca.shape)

df_cuaca = df_cuaca.drop_duplicates()

df_cuaca["forecast_time"] = pd.to_datetime(
    df_cuaca["forecast_time"],
    errors="coerce"
)

df_cuaca["utc_datetime"] = pd.to_datetime(
    df_cuaca["utc_datetime"],
    errors="coerce"
)

fitur_cuaca = [
    "temperature",
    "humidity",
    "wind_speed"
]

for kolom in fitur_cuaca:
    df_cuaca[kolom] = pd.to_numeric(
        df_cuaca[kolom],
        errors="coerce"
    )

df_cuaca = df_cuaca.dropna(
    subset=["forecast_time"]
)

print("Data setelah cleaning:", df_cuaca.shape)


# ------------------------------------------------------------
# 3.2 CLEANING DATA KONDISI LAUT
# ------------------------------------------------------------

print("\n[2] CLEANING DATA KONDISI LAUT")

print("Data sebelum cleaning:", df_utama.shape)

df_utama = df_utama.drop_duplicates()

df_utama["forecast_time"] = pd.to_datetime(
    df_utama["forecast_time"],
    errors="coerce"
)

fitur_laut = [
    "temperature",
    "humidity",
    "wind_speed",
    "wind_gust",
    "wave_height",
    "current_speed"
]

for kolom in fitur_laut:
    df_utama[kolom] = pd.to_numeric(
        df_utama[kolom],
        errors="coerce"
    )

df_utama = df_utama.dropna(
    subset=[
        "forecast_time",
        "wave_category"
    ]
)

print("Data setelah cleaning:", df_utama.shape)


# ------------------------------------------------------------
# 3.3 CLEANING DATA GEMPA
# ------------------------------------------------------------

print("\n[3] CLEANING DATA GEMPA")

print("Data sebelum cleaning:", df_gempa.shape)

df_gempa = df_gempa.drop_duplicates()

df_gempa["datetime_gempa"] = pd.to_datetime(
    df_gempa["datetime_gempa"],
    errors="coerce"
)

fitur_gempa = [
    "magnitude",
    "kedalaman_km",
    "latitude",
    "longitude"
]

for kolom in fitur_gempa:
    df_gempa[kolom] = pd.to_numeric(
        df_gempa[kolom],
        errors="coerce"
    )

df_gempa = df_gempa.dropna(
    subset=["datetime_gempa"]
)

print("Data setelah cleaning:", df_gempa.shape)


# ============================================================
# 4. ASSESSING SETELAH CLEANING
# ============================================================

print("\n" + "=" * 80)
print("4. ASSESSING DATA SETELAH CLEANING")
print("=" * 80)


# ------------------------------------------------------------
# 4.1 DATA CUACA
# ------------------------------------------------------------

print("\n--- DATA CUACA SETELAH CLEANING ---")

print("\nMissing values:")
print(df_cuaca.isnull().sum())

print("\nDuplikat:")
print(df_cuaca.duplicated().sum())

print("\nStatistik deskriptif:")
print(df_cuaca.describe(include="all"))


# ------------------------------------------------------------
# 4.2 DATA KONDISI LAUT
# ------------------------------------------------------------

print("\n--- DATA KONDISI LAUT SETELAH CLEANING ---")

print("\nMissing values:")
print(df_utama.isnull().sum())

print("\nDuplikat:")
print(df_utama.duplicated().sum())

print("\nStatistik deskriptif:")
print(df_utama.describe(include="all"))


# ------------------------------------------------------------
# 4.3 DATA GEMPA
# ------------------------------------------------------------

print("\n--- DATA GEMPA SETELAH CLEANING ---")

print("\nMissing values:")
print(df_gempa.isnull().sum())

print("\nDuplikat:")
print(df_gempa.duplicated().sum())

print("\nStatistik deskriptif:")
print(df_gempa.describe(include="all"))


# ============================================================
# 5. MENGAMBIL DATASET GABUNGAN YANG SUDAH ADA
# ============================================================

print("\n" + "=" * 80)
print("5. DATASET GABUNGAN HASIL DATA WRANGLING")
print("=" * 80)

conn = mysql.connector.connect(
    host="host.docker.internal",
    user="root",
    password="root",
    database="airflow_db"
)

query_gabungan = """
SELECT
    forecast_id,
    area_id,
    area_name,
    forecast_time,
    latitude,
    longitude,
    temperature,
    humidity,
    wind_speed,
    wind_gust,
    wave_height,
    current_speed,
    wave_category,
    jumlah_gempa_24jam,
    magnitude_maks_24jam,
    jarak_gempa_terdekat_km
FROM dataset_gabungan_gempa
ORDER BY forecast_time
"""

df = pd.read_sql(
    query_gabungan,
    conn
)

conn.close()

print("\nUkuran dataset gabungan:", df.shape)

print("\nKolom dataset gabungan:")
print(df.columns.tolist())

print("\n5 data pertama:")
print(df.head().to_string(index=False))


# ============================================================
# 6. ASSESSING DATASET GABUNGAN
# ============================================================

print("\n" + "=" * 80)
print("6. ASSESSING DATASET GABUNGAN")
print("=" * 80)

print("\n--- INFO ---")
df.info()

print("\n--- STATISTIK DESKRIPTIF ---")
print(df.describe(include="all"))

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- JUMLAH DUPLIKAT ---")
print(df.duplicated().sum())

print("\n--- 5 DATA PERTAMA ---")
print(df.head())


# ============================================================
# 7. CLEANING DATASET GABUNGAN
# ============================================================

print("\n" + "=" * 80)
print("7. CLEANING DATASET GABUNGAN")
print("=" * 80)

print("Data sebelum cleaning:", df.shape)

df = df.drop_duplicates()

df["forecast_time"] = pd.to_datetime(
    df["forecast_time"],
    errors="coerce"
)

df = df.dropna(
    subset=["wave_category"]
)


# ------------------------------------------------------------
# KONVERSI DATA NUMERIK
# ------------------------------------------------------------

fitur_numerik = [
    "latitude",
    "longitude",
    "temperature",
    "humidity",
    "wind_speed",
    "wind_gust",
    "wave_height",
    "current_speed",
    "jumlah_gempa_24jam",
    "magnitude_maks_24jam",
    "jarak_gempa_terdekat_km"
]

for kolom in fitur_numerik:
    df[kolom] = pd.to_numeric(
        df[kolom],
        errors="coerce"
    )

df = df.dropna(
    subset=fitur_numerik + ["forecast_time"]
)

print("Data setelah cleaning:", df.shape)


# ============================================================
# 8. ASSESSING AKHIR DATASET ANALISIS
# ============================================================

print("\n" + "=" * 80)
print("8. ASSESSING AKHIR DATASET ANALISIS")
print("=" * 80)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplikat:")
print(df.duplicated().sum())

print("\nStatistik numerik:")
print(df[fitur_numerik].describe())

print("\nDistribusi target:")
print(df["wave_category"].value_counts())


# ============================================================
# 9. FEATURE TAMBAHAN UNTUK ANALISIS WAKTU
# ============================================================

df["tanggal"] = df["forecast_time"].dt.date
df["jam"] = df["forecast_time"].dt.hour
df["hari"] = df["forecast_time"].dt.day_name()


# ============================================================
# 10. EDA - BUSINESS QUESTION 1
# ============================================================

print("\n" + "=" * 80)
print("10. EDA - BQ1")
print("=" * 80)

print("""
BQ1:
Bagaimana kondisi gelombang laut pada masing-masing wilayah
perairan berdasarkan data cuaca dan kondisi laut?
""")


# ------------------------------------------------------------
# VISUAL 1
# JUMLAH KATEGORI GELOMBANG PER WILAYAH
# ------------------------------------------------------------

tabel_bq1 = pd.crosstab(
    df["area_name"],
    df["wave_category"]
)

print("\nJumlah kategori gelombang per wilayah:")
print(tabel_bq1)

plt.figure(figsize=(12, 6))

sns.countplot(
    data=df,
    x="area_name",
    hue="wave_category"
)

plt.title(
    "Jumlah Kategori Kondisi Gelombang per Wilayah"
)

plt.xlabel("Wilayah Perairan")
plt.ylabel("Jumlah Pengamatan")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.legend(
    title="Kategori Gelombang"
)

plt.tight_layout()

plt.savefig(
    "bq1_01_jumlah_kategori_per_wilayah.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 2
# STACKED BAR PROPORSI KATEGORI
# ------------------------------------------------------------

proporsi_bq1 = pd.crosstab(
    df["area_name"],
    df["wave_category"],
    normalize="index"
) * 100

proporsi_bq1.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6)
)

plt.title(
    "Proporsi Kategori Kondisi Gelombang per Wilayah"
)

plt.xlabel("Wilayah Perairan")
plt.ylabel("Proporsi (%)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.legend(
    title="Kategori Gelombang"
)

plt.tight_layout()

plt.savefig(
    "bq1_02_proporsi_kategori_per_wilayah.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 3
# BOXPLOT TINGGI GELOMBANG PER WILAYAH
# ------------------------------------------------------------

plt.figure(figsize=(12, 6))

sns.boxplot(
    data=df,
    x="area_name",
    y="wave_height"
)

plt.title(
    "Distribusi Tinggi Gelombang per Wilayah"
)

plt.xlabel("Wilayah Perairan")
plt.ylabel("Tinggi Gelombang")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "bq1_03_boxplot_tinggi_gelombang_wilayah.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 4
# BOXPLOT KECEPATAN ANGIN PER WILAYAH
# ------------------------------------------------------------

plt.figure(figsize=(12, 6))

sns.boxplot(
    data=df,
    x="area_name",
    y="wind_speed"
)

plt.title(
    "Distribusi Kecepatan Angin per Wilayah"
)

plt.xlabel("Wilayah Perairan")
plt.ylabel("Kecepatan Angin")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "bq1_04_boxplot_angin_wilayah.png",
    dpi=300
)

plt.show()


# ============================================================
# 11. EDA - BUSINESS QUESTION 2
# ============================================================

print("\n" + "=" * 80)
print("11. EDA - BQ2")
print("=" * 80)

print("""
BQ2:
Bagaimana hubungan antara kecepatan angin, tinggi gelombang,
dan kecepatan arus terhadap kategori kondisi gelombang laut?
""")


# ------------------------------------------------------------
# VISUAL 5
# SCATTER KECEPATAN ANGIN VS TINGGI GELOMBANG
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=df,
    x="wind_speed",
    y="wave_height",
    hue="wave_category",
    style="wave_category",
    s=90
)

plt.title(
    "Hubungan Kecepatan Angin dan Tinggi Gelombang"
)

plt.xlabel("Kecepatan Angin")
plt.ylabel("Tinggi Gelombang")

plt.legend(
    title="Kategori Gelombang"
)

plt.tight_layout()

plt.savefig(
    "bq2_05_scatter_angin_vs_gelombang.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 6
# SCATTER KECEPATAN ARUS VS TINGGI GELOMBANG
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=df,
    x="current_speed",
    y="wave_height",
    hue="wave_category",
    style="wave_category",
    s=90
)

plt.title(
    "Hubungan Kecepatan Arus dan Tinggi Gelombang"
)

plt.xlabel("Kecepatan Arus")
plt.ylabel("Tinggi Gelombang")

plt.legend(
    title="Kategori Gelombang"
)

plt.tight_layout()

plt.savefig(
    "bq2_06_scatter_arus_vs_gelombang.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 7
# SCATTER KECEPATAN ANGIN VS KECEPATAN ARUS
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=df,
    x="wind_speed",
    y="current_speed",
    hue="wave_category",
    style="wave_category",
    s=90
)

plt.title(
    "Hubungan Kecepatan Angin dan Kecepatan Arus"
)

plt.xlabel("Kecepatan Angin")
plt.ylabel("Kecepatan Arus")

plt.legend(
    title="Kategori Gelombang"
)

plt.tight_layout()

plt.savefig(
    "bq2_07_scatter_angin_vs_arus.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 8
# CORRELATION HEATMAP
# ------------------------------------------------------------

kolom_korelasi = [
    "temperature",
    "humidity",
    "wind_speed",
    "wind_gust",
    "wave_height",
    "current_speed",
    "jumlah_gempa_24jam",
    "magnitude_maks_24jam",
    "jarak_gempa_terdekat_km"
]

plt.figure(figsize=(12, 8))

sns.heatmap(
    df[kolom_korelasi].corr(),
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0
)

plt.title(
    "Korelasi Faktor Cuaca, Kondisi Laut, dan Aktivitas Gempa"
)

plt.tight_layout()

plt.savefig(
    "bq2_08_correlation_heatmap.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 9
# BOXPLOT ANGIN BERDASARKAN KATEGORI
# ------------------------------------------------------------

plt.figure(figsize=(8, 6))

sns.boxplot(
    data=df,
    x="wave_category",
    y="wind_speed"
)

plt.title(
    "Kecepatan Angin Berdasarkan Kategori Gelombang"
)

plt.xlabel("Kategori Gelombang")
plt.ylabel("Kecepatan Angin")

plt.tight_layout()

plt.savefig(
    "bq2_09_boxplot_angin_kategori.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 10
# BOXPLOT ARUS BERDASARKAN KATEGORI
# ------------------------------------------------------------

plt.figure(figsize=(8, 6))

sns.boxplot(
    data=df,
    x="wave_category",
    y="current_speed"
)

plt.title(
    "Kecepatan Arus Berdasarkan Kategori Gelombang"
)

plt.xlabel("Kategori Gelombang")
plt.ylabel("Kecepatan Arus")

plt.tight_layout()

plt.savefig(
    "bq2_10_boxplot_arus_kategori.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 11
# BOXPLOT TEMPERATUR BERDASARKAN KATEGORI
# ------------------------------------------------------------

plt.figure(figsize=(8, 6))

sns.boxplot(
    data=df,
    x="wave_category",
    y="temperature"
)

plt.title(
    "Temperatur Berdasarkan Kategori Gelombang"
)

plt.xlabel("Kategori Gelombang")
plt.ylabel("Temperatur")

plt.tight_layout()

plt.savefig(
    "bq2_11_boxplot_temperature_kategori.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 12
# BOXPLOT HUMIDITY BERDASARKAN KATEGORI
# ------------------------------------------------------------

plt.figure(figsize=(8, 6))

sns.boxplot(
    data=df,
    x="wave_category",
    y="humidity"
)

plt.title(
    "Kelembapan Berdasarkan Kategori Gelombang"
)

plt.xlabel("Kategori Gelombang")
plt.ylabel("Kelembapan")

plt.tight_layout()

plt.savefig(
    "bq2_12_boxplot_humidity_kategori.png",
    dpi=300
)

plt.show()


# ============================================================
# 12. EDA - BUSINESS QUESTION 3
# ============================================================

print("\n" + "=" * 80)
print("12. EDA - BQ3")
print("=" * 80)

print("""
BQ3:
Bagaimana perbedaan kondisi gelombang laut berdasarkan lokasi
wilayah perairan dan waktu pengamatan?
""")


# ------------------------------------------------------------
# VISUAL 13
# VISUALISASI SPASIAL
# ------------------------------------------------------------

plt.figure(figsize=(10, 8))

sns.scatterplot(
    data=df,
    x="longitude",
    y="latitude",
    hue="wave_category",
    style="wave_category",
    size="wave_height",
    sizes=(50, 250),
    alpha=0.85
)

plt.title(
    "Distribusi Spasial Kondisi Gelombang Laut"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.legend(
    title="Kategori Gelombang"
)

plt.tight_layout()

plt.savefig(
    "bq3_13_spatial_gelombang.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 14
# PERUBAHAN TINGGI GELOMBANG BERDASARKAN WAKTU
# ------------------------------------------------------------

temporal_wave = (
    df.groupby("forecast_time")["wave_height"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(14, 6))

sns.lineplot(
    data=temporal_wave,
    x="forecast_time",
    y="wave_height",
    marker="o"
)

plt.title(
    "Perubahan Rata-rata Tinggi Gelombang Berdasarkan Waktu"
)

plt.xlabel("Waktu Pengamatan")
plt.ylabel("Rata-rata Tinggi Gelombang")

plt.xticks(
    rotation=45
)

plt.tight_layout()

plt.savefig(
    "bq3_14_temporal_tinggi_gelombang.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 15
# JUMLAH KONDISI GELOMBANG BERDASARKAN WAKTU
# ------------------------------------------------------------

temporal_category = (
    df.groupby(
        [
            pd.Grouper(
                key="forecast_time",
                freq="D"
            ),
            "wave_category"
        ]
    )
    .size()
    .reset_index(
        name="jumlah"
    )
)

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=temporal_category,
    x="forecast_time",
    y="jumlah",
    hue="wave_category",
    marker="o"
)

plt.title(
    "Perubahan Kategori Kondisi Gelombang Berdasarkan Waktu"
)

plt.xlabel("Tanggal Pengamatan")
plt.ylabel("Jumlah Pengamatan")

plt.xticks(
    rotation=45
)

plt.legend(
    title="Kategori Gelombang"
)

plt.tight_layout()

plt.savefig(
    "bq3_15_temporal_kategori_gelombang.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# VISUAL 16
# HEATMAP WILAYAH × TANGGAL
# ------------------------------------------------------------

heatmap_waktu = df.pivot_table(
    index="area_name",
    columns="tanggal",
    values="wave_height",
    aggfunc="mean"
)

plt.figure(figsize=(12, 7))

sns.heatmap(
    heatmap_waktu,
    annot=True,
    fmt=".2f",
    cmap="YlOrRd"
)

plt.title(
    "Rata-rata Tinggi Gelombang Berdasarkan Wilayah dan Tanggal"
)

plt.xlabel("Tanggal")
plt.ylabel("Wilayah Perairan")

plt.tight_layout()

plt.savefig(
    "bq3_16_heatmap_wilayah_waktu.png",
    dpi=300
)

plt.show()


# ============================================================
# 13. FEATURE ENGINEERING UNTUK MACHINE LEARNING
# ============================================================

print("\n" + "=" * 80)
print("13. FEATURE ENGINEERING")
print("=" * 80)


# ------------------------------------------------------------
# FITUR WAKTU
# ------------------------------------------------------------

df["hour"] = df["forecast_time"].dt.hour

df["day_of_week"] = (
    df["forecast_time"].dt.dayofweek
)

print("\nFitur waktu berhasil dibuat.")

print(
    df[
        [
            "forecast_time",
            "hour",
            "day_of_week"
        ]
    ].head()
)


# ============================================================
# 14. MACHINE LEARNING - DECISION TREE
# ============================================================

print("\n" + "=" * 80)
print("14. MACHINE LEARNING - DECISION TREE")
print("=" * 80)

print("""
BQ4:
Dapatkah kondisi gelombang laut diklasifikasikan menjadi kategori
Tenang dan Rendah berdasarkan faktor cuaca, kondisi laut, lokasi,
waktu, dan aktivitas gempa?
""")


# ------------------------------------------------------------
# FITUR MODEL
# ------------------------------------------------------------
#
# wave_height TIDAK dimasukkan sebagai fitur model
# karena sangat berkaitan dengan pembentukan kategori gelombang
# dan dapat menyebabkan target leakage.
#
# wave_height tetap digunakan pada tahap EDA.
# ------------------------------------------------------------

fitur = [

    # lokasi
    "latitude",
    "longitude",

    # waktu
    "hour",
    "day_of_week",

    # cuaca
    "temperature",
    "humidity",
    "wind_speed",
    "wind_gust",

    # kondisi laut
    "current_speed",

    # aktivitas gempa
    "jumlah_gempa_24jam",
    "magnitude_maks_24jam",
    "jarak_gempa_terdekat_km"
]


target = "wave_category"

X = df[fitur]

y = df[target]


print("\nJumlah fitur:", len(fitur))

print("\nFitur yang digunakan:")

for nomor, nama_fitur in enumerate(
    fitur,
    start=1
):
    print(
        f"{nomor}. {nama_fitur}"
    )


print("\nDistribusi target:")
print(y.value_counts())


# ============================================================
# 15. TRAIN TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


print("\n" + "=" * 80)
print("TRAIN TEST SPLIT")
print("=" * 80)

print("Data training :", X_train.shape)
print("Data testing  :", X_test.shape)


# ============================================================
# 16. PIPELINE DECISION TREE
# ============================================================

model = Pipeline(
    steps=[

        (
            "scaler",
            StandardScaler()
        ),

        (
            "classifier",
            DecisionTreeClassifier(

                criterion="gini",

                max_depth=4,

                min_samples_split=10,

                min_samples_leaf=5,

                random_state=42,

                class_weight="balanced"
            )
        )
    ]
)


# ============================================================
# 17. TRAINING MODEL
# ============================================================

print("\n" + "=" * 80)
print("TRAINING MODEL")
print("=" * 80)

model.fit(
    X_train,
    y_train
)

print("Training selesai.")


# ============================================================
# 18. PREDIKSI
# ============================================================

y_pred = model.predict(
    X_test
)


# ============================================================
# 19. EVALUASI MODEL
# ============================================================

print("\n" + "=" * 80)
print("EVALUASI MODEL")
print("=" * 80)


# ------------------------------------------------------------
# ACCURACY
# ------------------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


# ------------------------------------------------------------
# CLASSIFICATION REPORT
# ------------------------------------------------------------

print("\n--- CLASSIFICATION REPORT ---")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# ------------------------------------------------------------
# CONFUSION MATRIX
# ------------------------------------------------------------

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\n--- CONFUSION MATRIX ---")

print(cm)

plt.figure(
    figsize=(7, 6)
)

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=model.classes_,
    yticklabels=model.classes_
)

plt.title(
    "Confusion Matrix - Decision Tree"
)

plt.xlabel(
    "Predicted"
)

plt.ylabel(
    "Actual"
)

plt.tight_layout()

plt.savefig(
    "17_confusion_matrix_decision_tree.png",
    dpi=300
)

plt.show()


# ============================================================
# 20. CROSS VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("5-FOLD CROSS VALIDATION")
print("=" * 80)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=cv,
    scoring="accuracy"
)

print("\nAccuracy setiap fold:")

for nomor, skor in enumerate(
    cv_scores,
    start=1
):

    print(
        f"Fold {nomor}: {skor:.4f}"
    )


print(
    f"\nRata-rata accuracy: "
    f"{cv_scores.mean():.4f}"
)

print(
    f"Standar deviasi: "
    f"{cv_scores.std():.4f}"
)


# ============================================================
# 21. FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 80)
print("FEATURE IMPORTANCE")
print("=" * 80)

classifier = model.named_steps[
    "classifier"
]

importance = classifier.feature_importances_

feature_importance = pd.DataFrame({

    "feature": fitur,

    "importance": importance

}).sort_values(
    by="importance",
    ascending=False
)


print(
    feature_importance.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# VISUAL 18
# FEATURE IMPORTANCE
# ------------------------------------------------------------

plt.figure(
    figsize=(10, 7)
)

sns.barplot(
    data=feature_importance,
    x="importance",
    y="feature"
)

plt.title(
    "Feature Importance - Decision Tree"
)

plt.xlabel(
    "Importance"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

plt.savefig(
    "18_feature_importance_decision_tree.png",
    dpi=300
)

plt.show()


# ============================================================
# 22. VISUALISASI POHON KEPUTUSAN
# ============================================================

print("\n" + "=" * 80)
print("VISUALISASI DECISION TREE")
print("=" * 80)

plt.figure(
    figsize=(24, 14)
)

plot_tree(

    classifier,

    feature_names=fitur,

    class_names=classifier.classes_,

    filled=True,

    rounded=True,

    fontsize=9
)

plt.title(
    "Decision Tree - Klasifikasi Kondisi Gelombang Laut"
)

plt.tight_layout()

plt.savefig(
    "19_visualisasi_decision_tree.png",
    dpi=300
)

plt.show()


# ============================================================
# 23. INFORMASI STRUKTUR DECISION TREE
# ============================================================

print("\n" + "=" * 80)
print("INFORMASI DECISION TREE")
print("=" * 80)

print(
    "Max depth:",
    classifier.max_depth
)

print(
    "Actual tree depth:",
    classifier.tree_.max_depth
)

print(
    "Jumlah leaves:",
    classifier.get_n_leaves()
)


# ============================================================
# 24. CONTOH HASIL PREDIKSI
# ============================================================

print("\n" + "=" * 80)
print("CONTOH HASIL PREDIKSI")
print("=" * 80)

hasil_prediksi = X_test.copy()

hasil_prediksi["aktual"] = y_test.values

hasil_prediksi["prediksi"] = y_pred

print(
    hasil_prediksi.head(10).to_string()
)


# ============================================================
# 25. SIMPAN HASIL PREDIKSI
# ============================================================

hasil_prediksi.to_csv(
    "hasil_prediksi_klasifikasi.csv",
    index=False
)

print(
    "\nFile hasil_prediksi_klasifikasi.csv berhasil dibuat."
)


# ============================================================
# 26. RINGKASAN HASIL
# ============================================================

print("\n" + "=" * 80)
print("RINGKASAN HASIL PROYEK")
print("=" * 80)

print(
    f"\nJumlah data akhir       : {len(df)}"
)

print(
    f"Jumlah fitur ML         : {len(fitur)}"
)

print(
    f"Jumlah data training    : {len(X_train)}"
)

print(
    f"Jumlah data testing     : {len(X_test)}"
)

print(
    f"Accuracy Decision Tree  : {accuracy * 100:.2f}%"
)

print(
    f"CV Mean Accuracy        : {cv_scores.mean() * 100:.2f}%"
)

print(
    f"CV Std                  : {cv_scores.std():.4f}"
)

print("\nFeature paling berpengaruh:")

print(
    feature_importance.head(5).to_string(
        index=False
    )
)


# ============================================================
# SELESAI
# ============================================================

print("\n" + "=" * 80)
print("SELURUH PROSES SELESAI")
print("=" * 80)

print("""
VISUALISASI YANG DIHASILKAN:

BQ1 - Kondisi Gelombang per Wilayah
1.  bq1_01_jumlah_kategori_per_wilayah.png
2.  bq1_02_proporsi_kategori_per_wilayah.png
3.  bq1_03_boxplot_tinggi_gelombang_wilayah.png
4.  bq1_04_boxplot_angin_wilayah.png

BQ2 - Hubungan Faktor Cuaca dan Kondisi Laut
5.  bq2_05_scatter_angin_vs_gelombang.png
6.  bq2_06_scatter_arus_vs_gelombang.png
7.  bq2_07_scatter_angin_vs_arus.png
8.  bq2_08_correlation_heatmap.png
9.  bq2_09_boxplot_angin_kategori.png
10. bq2_10_boxplot_arus_kategori.png
11. bq2_11_boxplot_temperature_kategori.png
12. bq2_12_boxplot_humidity_kategori.png

BQ3 - Lokasi dan Waktu
13. bq3_13_spatial_gelombang.png
14. bq3_14_temporal_tinggi_gelombang.png
15. bq3_15_temporal_kategori_gelombang.png
16. bq3_16_heatmap_wilayah_waktu.png

Machine Learning
17. 17_confusion_matrix_decision_tree.png
18. 18_feature_importance_decision_tree.png
19. 19_visualisasi_decision_tree.png

Output
20. hasil_prediksi_klasifikasi.csv
""")

print("=" * 80)