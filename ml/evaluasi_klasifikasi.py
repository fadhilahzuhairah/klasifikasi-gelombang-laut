import pandas as pd
import mysql.connector
from math import radians, sin, cos, sqrt, atan2


# ============================================================
# 1. KONEKSI KE DATABASE MYSQL
# ============================================================

conn = mysql.connector.connect(
    host="host.docker.internal",
    port=3306,
    user="root",
    password="root",
    database="airflow_db"
)

print("Koneksi MySQL berhasil.")


# ============================================================
# 2. AMBIL DATA UTAMA
# ============================================================

query_utama = """
SELECT
    forecast_id,
    area_id,
    area_name,
    forecast_time,
    weather,
    temperature,
    humidity,
    wind_speed,
    wind_gust,
    wave_category,
    wave_height,
    current_speed
FROM marine_data_utama
"""

df_utama = pd.read_sql(
    query_utama,
    conn
)

print("Data utama berhasil diambil.")
print("Jumlah data utama:", len(df_utama))


# ============================================================
# 3. AMBIL DATA GEMPA
# ============================================================

query_gempa = """
SELECT
    gempa_id,
    datetime_gempa,
    magnitude,
    latitude,
    longitude
FROM marine_data_gempa
"""

df_gempa = pd.read_sql(
    query_gempa,
    conn
)

print("Data gempa berhasil diambil.")
print("Jumlah data gempa:", len(df_gempa))


# ============================================================
# 4. KOORDINAT REPRESENTATIF WILAYAH PERAIRAN
# ============================================================

koordinat = {
    "P.AF.01": (-3.46, 122.43),
    "P.AF.02": (-3.35, 122.55),
    "P.AF.04": (-4.00, 122.65),
    "P.AF.05": (-4.20, 122.95),
    "P.AF.13": (-5.00, 122.80),
    "P.AF.14": (-3.50, 121.80),
    "P.AF.19": (-5.30, 123.80),
}


df_utama["latitude"] = df_utama["area_id"].map(
    lambda x: koordinat.get(x, (None, None))[0]
)

df_utama["longitude"] = df_utama["area_id"].map(
    lambda x: koordinat.get(x, (None, None))[1]
)


# ============================================================
# 5. KONVERSI DATETIME
# ============================================================

df_utama["forecast_time"] = pd.to_datetime(
    df_utama["forecast_time"]
)

df_gempa["datetime_gempa"] = pd.to_datetime(
    df_gempa["datetime_gempa"]
)


# ============================================================
# 6. FUNGSI MENGHITUNG JARAK
# ============================================================

def hitung_jarak(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


# ============================================================
# 7. MEMBUAT FITUR GEMPA SPASIAL-TEMPORAL
# ============================================================

jumlah_gempa = []
magnitude_maks = []
jarak_terdekat = []


for _, row in df_utama.iterrows():

    waktu_forecast = row["forecast_time"]

    lat_area = row["latitude"]
    lon_area = row["longitude"]


    # --------------------------------------------------------
    # Ambil gempa 24 jam sebelum waktu forecast
    # --------------------------------------------------------

    gempa_24jam = df_gempa[
        (df_gempa["datetime_gempa"] <= waktu_forecast)
        &
        (
            df_gempa["datetime_gempa"]
            >= waktu_forecast - pd.Timedelta(hours=24)
        )
    ].copy()


    # --------------------------------------------------------
    # Jika tidak ada gempa
    # --------------------------------------------------------

    if gempa_24jam.empty:

        jumlah_gempa.append(0)

        magnitude_maks.append(0)

        jarak_terdekat.append(9999)

        continue


    # --------------------------------------------------------
    # Jumlah gempa
    # --------------------------------------------------------

    jumlah_gempa.append(
        len(gempa_24jam)
    )


    # --------------------------------------------------------
    # Magnitude maksimum
    # --------------------------------------------------------

    magnitude_maks.append(
        gempa_24jam["magnitude"].max()
    )


    # --------------------------------------------------------
    # Hitung jarak gempa
    # --------------------------------------------------------

    jarak_list = []


    for _, gempa in gempa_24jam.iterrows():

        if (
            pd.isna(gempa["latitude"])
            or pd.isna(gempa["longitude"])
            or pd.isna(lat_area)
            or pd.isna(lon_area)
        ):
            continue


        jarak = hitung_jarak(
            lat_area,
            lon_area,
            gempa["latitude"],
            gempa["longitude"]
        )

        jarak_list.append(jarak)


    # --------------------------------------------------------
    # Jarak gempa terdekat
    # --------------------------------------------------------

    if len(jarak_list) == 0:

        jarak_terdekat.append(9999)

    else:

        jarak_terdekat.append(
            min(jarak_list)
        )


# ============================================================
# 8. TAMBAHKAN FITUR GEMPA KE DATA UTAMA
# ============================================================

df_utama["jumlah_gempa_24jam"] = jumlah_gempa

df_utama["magnitude_maks_24jam"] = magnitude_maks

df_utama["jarak_gempa_terdekat_km"] = jarak_terdekat


# ============================================================
# 9. TAMPILKAN DATASET HASIL GABUNGAN
# ============================================================

print()
print("============================================================")
print("              DATASET HASIL GABUNGAN")
print("============================================================")


kolom_hasil = [
    "forecast_id",
    "area_id",
    "area_name",
    "forecast_time",
    "weather",
    "temperature",
    "humidity",
    "wind_speed",
    "wind_gust",
    "wave_category",
    "wave_height",
    "current_speed",
    "latitude",
    "longitude",
    "jumlah_gempa_24jam",
    "magnitude_maks_24jam",
    "jarak_gempa_terdekat_km"
]


print(
    df_utama[
        kolom_hasil
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 10. INFORMASI FITUR GEMPA
# ============================================================

print()
print("============================================================")
print("                INFORMASI FITUR GEMPA")
print("============================================================")


print("\nJumlah gempa 24 jam:")

print(
    df_utama["jumlah_gempa_24jam"]
    .describe()
)


print("\nMagnitude maksimum 24 jam:")

print(
    df_utama["magnitude_maks_24jam"]
    .describe()
)


print("\nJarak gempa terdekat:")

print(
    df_utama["jarak_gempa_terdekat_km"]
    .describe()
)


# ============================================================
# 11. DATA YANG MEMILIKI GEMPA
# ============================================================

data_dengan_gempa = df_utama[
    df_utama["jumlah_gempa_24jam"] > 0
]


print()
print("============================================================")
print("             DATA YANG MEMILIKI GEMPA")
print("============================================================")


print(
    "Jumlah baris dengan gempa:",
    len(data_dengan_gempa)
)


if len(data_dengan_gempa) > 0:

    print(
        data_dengan_gempa[
            [
                "forecast_id",
                "area_name",
                "forecast_time",
                "jumlah_gempa_24jam",
                "magnitude_maks_24jam",
                "jarak_gempa_terdekat_km"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

else:

    print("Tidak ada data forecast yang memiliki gempa dalam 24 jam sebelumnya.")


# ============================================================
# 12. SIMPAN DATASET HASIL GABUNGAN
# ============================================================

output_file = "ml/dataset_gabungan_gempa.csv"

df_utama.to_csv(
    output_file,
    index=False
)

print()
print("Dataset gabungan disimpan ke:")
print(output_file)


# ============================================================
# 13. TUTUP KONEKSI
# ============================================================

conn.close()

print()
print("Koneksi MySQL ditutup.")
print("Proses selesai.")