from datetime import datetime

import json
import requests

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook


BASE_URL = "https://maritim.bmkg.go.id/marine2026-data/perairan/"

# =========================================================
# WILAYAH PERAIRAN SULAWESI TENGGARA
# =========================================================

SULTRA_AREAS = [
    ("P.AF.19", "Laut Banda Timur Wakatobi"),
    ("P.AF.13", "Perairan Buton"),
    ("P.AF.14", "Teluk Bone Barat Kolaka Utara"),
    ("P.AF.01", "Selat Labengki"),
    ("P.AF.02", "Laut Labengki"),
    ("P.AF.04", "Teluk Kendari - Moramo"),
    ("P.AF.05", "Selat Wawoni"),
]


OUTPUT_FILE = "/usr/local/airflow/include/marine_transformed.json"


# =========================================================
# HELPER
# =========================================================

def convert_bmkg_datetime(value):
    """
    Mengubah format:
    2026-09-28 00:00 UTC

    menjadi:
    2026-09-28 00:00:00

    agar bisa disimpan ke MySQL DATETIME.
    """

    if not value:
        return None

    value = value.replace(" UTC", "").strip()

    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


# =========================================================
# 1. CREATE 3 TABLES
# =========================================================

def create_table():

    hook = MySqlHook(mysql_conn_id="mysql-local")

    # -----------------------------------------------------
    # TABLE 1: marine_areas
    # -----------------------------------------------------

    hook.run(
        """
        CREATE TABLE IF NOT EXISTS marine_areas (
            area_id VARCHAR(20) PRIMARY KEY,
            area_name VARCHAR(150) NOT NULL
        )
        """
    )

    # -----------------------------------------------------
    # TABLE 2: marine_forecast
    # -----------------------------------------------------

    hook.run(
        """
        CREATE TABLE IF NOT EXISTS marine_forecast (
            forecast_id INT AUTO_INCREMENT PRIMARY KEY,

            area_id VARCHAR(20) NOT NULL,

            forecast_time DATETIME NOT NULL,

            weather VARCHAR(100),
            temperature FLOAT,
            humidity FLOAT,

            issued_at DATETIME,
            valid_from DATETIME,
            valid_to DATETIME,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE KEY unique_forecast (
                area_id,
                forecast_time
            ),

            CONSTRAINT fk_forecast_area
                FOREIGN KEY (area_id)
                REFERENCES marine_areas(area_id)
                ON DELETE CASCADE
        )
        """
    )

    # -----------------------------------------------------
    # TABLE 3: marine_conditions
    # -----------------------------------------------------

    hook.run(
        """
        CREATE TABLE IF NOT EXISTS marine_conditions (
            condition_id INT AUTO_INCREMENT PRIMARY KEY,

            forecast_id INT NOT NULL,

            wind_direction VARCHAR(50),
            wind_speed FLOAT,
            wind_gust FLOAT,

            wave_category VARCHAR(50),
            wave_height FLOAT,

            current_direction VARCHAR(50),
            current_speed FLOAT,

            UNIQUE KEY unique_condition (
                forecast_id
            ),

            CONSTRAINT fk_conditions_forecast
                FOREIGN KEY (forecast_id)
                REFERENCES marine_forecast(forecast_id)
                ON DELETE CASCADE
        )
        """
    )

    print("3 tabel berhasil dibuat:")
    print("- marine_areas")
    print("- marine_forecast")
    print("- marine_conditions")


# =========================================================
# 2. EXTRACT + TRANSFORM
# =========================================================

def extract_transform():

    all_data = []

    for area_id, area_name in SULTRA_AREAS:

        url = f"{BASE_URL}{area_id}.json"

        print(f"Mengambil data: {area_name}")
        print(f"URL: {url}")

        response = requests.get(
            url,
            headers={
                "User-Agent": "FlowPraktikum/1.0"
            },
            timeout=60,
        )

        response.raise_for_status()

        result = response.json()

        # -------------------------------------------------
        # Metadata waktu
        # -------------------------------------------------

        issued_at = convert_bmkg_datetime(
            result.get("issued")
        )

        valid_from = convert_bmkg_datetime(
            result.get("valid_from")
        )

        valid_to = convert_bmkg_datetime(
            result.get("valid_to")
        )

        # -------------------------------------------------
        # Gabungkan forecast day 1 dan day 2-4
        # -------------------------------------------------

        forecast = []

        forecast.extend(
            result.get("forecast_day1", [])
        )

        forecast.extend(
            result.get("forecast_day2-4", [])
        )

        # -------------------------------------------------
        # Transform setiap data forecast
        # -------------------------------------------------

        for item in forecast:

            forecast_time = convert_bmkg_datetime(
                item.get("time")
            )

            row = {
                "area_id": area_id,
                "area_name": area_name,

                "forecast_time": forecast_time,

                "weather": item.get("weather"),
                "temperature": item.get("temp_avg"),
                "humidity": item.get("rh_avg"),

                "wind_direction": item.get("wind_from"),
                "wind_speed": item.get("wind_speed"),
                "wind_gust": item.get("wind_gust"),

                "wave_category": item.get("wave_cat"),
                "wave_height": item.get("wave_height"),

                "current_direction": item.get("current_to"),
                "current_speed": item.get("current_speed"),

                "issued_at": issued_at,
                "valid_from": valid_from,
                "valid_to": valid_to,
            }

            all_data.append(row)

    print(
        f"Total data setelah transform: "
        f"{len(all_data)}"
    )

    # -----------------------------------------------------
    # Simpan hasil transform
    # -----------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            all_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        "Data hasil transform berhasil "
        "disimpan ke marine_transformed.json"
    )


# =========================================================
# 3. LOAD TO MYSQL
# =========================================================

def load_to_mysql():

    # -----------------------------------------------------
    # Baca hasil transform
    # -----------------------------------------------------

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    hook = MySqlHook(
        mysql_conn_id="mysql-local"
    )

    # =====================================================
    # A. LOAD TABLE marine_areas
    # =====================================================

    area_sql = """
        INSERT INTO marine_areas (
            area_id,
            area_name
        )
        VALUES (
            %s,
            %s
        )
        ON DUPLICATE KEY UPDATE
            area_name = VALUES(area_name)
    """

    area_values = {}

    for row in data:

        area_id = row["area_id"]

        if area_id not in area_values:

            area_values[area_id] = (
                area_id,
                row["area_name"]
            )

    for values in area_values.values():

        hook.run(
            area_sql,
            parameters=values,
        )

    print(
        f"{len(area_values)} wilayah berhasil "
        f"dimasukkan ke marine_areas."
    )

    # =====================================================
    # B. LOAD TABLE marine_forecast
    # =====================================================

    forecast_sql = """
        INSERT INTO marine_forecast (
            area_id,
            forecast_time,
            weather,
            temperature,
            humidity,
            issued_at,
            valid_from,
            valid_to
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE

            weather = VALUES(weather),
            temperature = VALUES(temperature),
            humidity = VALUES(humidity),

            issued_at = VALUES(issued_at),
            valid_from = VALUES(valid_from),
            valid_to = VALUES(valid_to)
    """

    for row in data:

        values = (
            row["area_id"],
            row["forecast_time"],
            row["weather"],
            row["temperature"],
            row["humidity"],
            row["issued_at"],
            row["valid_from"],
            row["valid_to"],
        )

        hook.run(
            forecast_sql,
            parameters=values,
        )

    print(
        "Data berhasil dimasukkan "
        "ke marine_forecast."
    )

    # =====================================================
    # C. LOAD TABLE marine_conditions
    # =====================================================

    condition_sql = """
        INSERT INTO marine_conditions (
            forecast_id,
            wind_direction,
            wind_speed,
            wind_gust,
            wave_category,
            wave_height,
            current_direction,
            current_speed
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE

            wind_direction = VALUES(wind_direction),
            wind_speed = VALUES(wind_speed),
            wind_gust = VALUES(wind_gust),

            wave_category = VALUES(wave_category),
            wave_height = VALUES(wave_height),

            current_direction = VALUES(current_direction),
            current_speed = VALUES(current_speed)
    """

    # -----------------------------------------------------
    # Ambil forecast_id untuk setiap data
    # -----------------------------------------------------

    select_forecast_id_sql = """
        SELECT forecast_id
        FROM marine_forecast
        WHERE area_id = %s
          AND forecast_time = %s
    """

    condition_count = 0

    for row in data:

        result = hook.get_first(
            select_forecast_id_sql,
            parameters=(
                row["area_id"],
                row["forecast_time"],
            ),
        )

        if not result:
            print(
                "WARNING: forecast_id tidak ditemukan "
                f"untuk {row['area_id']} "
                f"{row['forecast_time']}"
            )
            continue

        forecast_id = result[0]

        values = (
            forecast_id,

            row["wind_direction"],
            row["wind_speed"],
            row["wind_gust"],

            row["wave_category"],
            row["wave_height"],

            row["current_direction"],
            row["current_speed"],
        )

        hook.run(
            condition_sql,
            parameters=values,
        )

        condition_count += 1

    print(
        f"{condition_count} data kondisi berhasil "
        "dimasukkan ke marine_conditions."
    )

    print("====================================")
    print("LOAD SELESAI")
    print("3 tabel berhasil diisi.")
    print("====================================")


# =========================================================
# DAG
# =========================================================

with DAG(
    dag_id="bmkg_maritim_etl",

    start_date=datetime(
        2026,
        1,
        1,
    ),

    schedule="0 * * * *",

    catchup=False,

    tags=[
        "bmkg",
        "maritim",
        "sulawesi-tenggara",
    ],
) as dag:

    create = PythonOperator(
        task_id="create_table",

        python_callable=create_table,
    )

    extract_transform_task = PythonOperator(
        task_id="extract_transform",

        python_callable=extract_transform,
    )

    load = PythonOperator(
        task_id="load_to_mysql",

        python_callable=load_to_mysql,
    )

    create >> extract_transform_task >> load