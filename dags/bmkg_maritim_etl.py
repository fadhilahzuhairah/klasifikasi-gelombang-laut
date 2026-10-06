from datetime import datetime
import json
import re
import requests

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook


# =========================================================
# CONFIG
# =========================================================

BASE_MARITIM_URL = (
    "https://maritim.bmkg.go.id/marine2026-data/perairan/"
)

BASE_WEATHER_URL = (
    "https://api.bmkg.go.id/publik/prakiraan-cuaca"
)

BASE_GEMPA_URL = (
    "https://data.bmkg.go.id/DataMKG/TEWS/"
)

OUTPUT_FILE = (
    "/usr/local/airflow/include/marine_transformed.json"
)


# =========================================================
# DATA UTAMA
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


# =========================================================
# DATA CUACA PENDUKUNG
# =========================================================
# Kode ADM4 menggunakan kode wilayah tingkat IV BMKG.
# Beberapa kode lama menghasilkan 404 sehingga diperbaiki.
# =========================================================

WEATHER_LOCATIONS = [
    {
        "adm4": "74.07.01.1001",
        "location_name": "Wanci",
        "related_area": "Wakatobi",
    },
    {
        "adm4": "74.14.01.2001",
        "location_name": "Pasarwajo",
        "related_area": "Buton",
    },
    {
        "adm4": "74.08.01.1001",
        "location_name": "Lasusua",
        "related_area": "Kolaka Utara",
    },
    {
        "adm4": "74.09.01.2005",
        "location_name": "Wanggudu",
        "related_area": "Konawe Utara",
    },
    {
        "adm4": "74.05.10.2013",
        "location_name": "Moramo",
        "related_area": "Konawe Selatan",
    },
    {
        "adm4": "74.10.01.2001",
        "location_name": "Langara",
        "related_area": "Konawe Kepulauan",
    },
    {
        "adm4": "74.71.06.1001",
        "location_name": "Puday",
        "related_area": "Kota Kendari",
    },
]


# =========================================================
# HELPER DATETIME
# =========================================================

def convert_bmkg_datetime(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    # -----------------------------------------------------
    # NORMALISASI FORMAT BMKG
    # -----------------------------------------------------

    value = value.replace("T", " ")
    value = value.replace("Z", "")

    value = re.sub(
        r"\s*UTC\s*$",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\s*GMT\s*$",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = value.strip()

    # -----------------------------------------------------
    # PARSE DATETIME
    # -----------------------------------------------------

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]

    for fmt in formats:

        try:

            dt = datetime.strptime(
                value,
                fmt,
            )

            return dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:
            continue

    # -----------------------------------------------------
    # COBA AMBIL BAGIAN DATETIME DENGAN REGEX
    # -----------------------------------------------------

    match = re.search(
        r"(\d{4}-\d{2}-\d{2})\s+"
        r"(\d{2}:\d{2}(?::\d{2})?)",
        value,
    )

    if match:

        date_part = match.group(1)
        time_part = match.group(2)

        if len(time_part) == 5:
            time_part += ":00"

        return f"{date_part} {time_part}"

    print(
        f"WARNING: format datetime tidak dikenali: {value}"
    )

    return None


# =========================================================
# HELPER NUMBER
# =========================================================

def parse_number(value):

    if value is None:
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


# =========================================================
# HTTP GET HELPER
# =========================================================

def get_json(url, params=None):

    response = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "FlowPraktikum/1.0"
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# 1. CREATE TABLE
# =========================================================

def create_table():

    hook = MySqlHook(
        mysql_conn_id="mysql-local"
    )

    # =====================================================
    # TABLE UTAMA
    # =====================================================

    hook.run(
        """
        CREATE TABLE IF NOT EXISTS marine_data_utama (

            forecast_id INT AUTO_INCREMENT PRIMARY KEY,

            area_id VARCHAR(20) NOT NULL,

            area_name VARCHAR(150) NOT NULL,

            forecast_time DATETIME NOT NULL,

            weather VARCHAR(100),

            temperature FLOAT,

            humidity FLOAT,

            wind_direction VARCHAR(50),

            wind_speed FLOAT,

            wind_gust FLOAT,

            wave_category VARCHAR(50),

            wave_height FLOAT,

            current_direction VARCHAR(50),

            current_speed FLOAT,

            issued_at DATETIME,

            valid_from DATETIME,

            valid_to DATETIME,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE KEY unique_forecast (
                area_id,
                forecast_time
            )

        )
        """
    )

    # =====================================================
    # TABLE GEMPA
    # =====================================================

    hook.run(
        """
        CREATE TABLE IF NOT EXISTS marine_data_gempa (

            gempa_id INT AUTO_INCREMENT PRIMARY KEY,

            source VARCHAR(20),

            tanggal VARCHAR(20),

            jam VARCHAR(20),

            datetime_gempa DATETIME,

            magnitude FLOAT,

            kedalaman_km FLOAT,

            latitude FLOAT,

            longitude FLOAT,

            wilayah VARCHAR(255),

            potensi VARCHAR(255),

            dirasakan VARCHAR(255),

            shakemap VARCHAR(255),

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE KEY unique_gempa (
                datetime_gempa,
                magnitude,
                latitude,
                longitude
            )

        )
        """
    )

    # =====================================================
    # TABLE CUACA
    # =====================================================

    hook.run(
        """
        CREATE TABLE IF NOT EXISTS marine_data_cuaca (

            cuaca_id INT AUTO_INCREMENT PRIMARY KEY,

            adm4 VARCHAR(30),

            location_name VARCHAR(150),

            related_area VARCHAR(150),

            forecast_time DATETIME,

            utc_datetime DATETIME,

            weather VARCHAR(100),

            temperature FLOAT,

            humidity FLOAT,

            wind_speed FLOAT,

            visibility VARCHAR(100),

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE KEY unique_cuaca (
                adm4,
                forecast_time
            )

        )
        """
    )

    print("====================================")
    print("3 tabel berhasil dibuat:")
    print("")
    print("1. marine_data_utama")
    print("2. marine_data_gempa")
    print("3. marine_data_cuaca")
    print("====================================")


# =========================================================
# 2. EXTRACT + TRANSFORM
# =========================================================

def extract_transform():

    data_utama = []
    data_gempa = []
    data_cuaca = []

    # =====================================================
    # A. DATA UTAMA MARITIM SULAWESI TENGGARA
    # =====================================================

    print("")
    print("====================================")
    print("EXTRACT DATA UTAMA MARITIM SULTRA")
    print("====================================")

    for area_id, area_name in SULTRA_AREAS:

        url = (
            f"{BASE_MARITIM_URL}"
            f"{area_id}.json"
        )

        print("")
        print(f"Mengambil: {area_name}")
        print(f"URL: {url}")

        try:

            result = get_json(url)

        except Exception as error:

            print(
                f"GAGAL mengambil "
                f"{area_name}: {error}"
            )

            continue

        # -------------------------------------------------
        # METADATA
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
        # FORECAST
        # -------------------------------------------------

        forecast = []

        forecast.extend(
            result.get(
                "forecast_day1",
                []
            )
        )

        forecast.extend(
            result.get(
                "forecast_day2-4",
                []
            )
        )

        # -------------------------------------------------
        # TRANSFORM
        # -------------------------------------------------

        for item in forecast:

            forecast_time = (
                convert_bmkg_datetime(
                    item.get("time")
                )
            )

            if forecast_time is None:

                print(
                    "WARNING: forecast_time "
                    "tidak valid, data dilewati:"
                )

                print(item)

                continue

            row = {

                "area_id":
                    area_id,

                "area_name":
                    area_name,

                "forecast_time":
                    forecast_time,

                "weather":
                    item.get("weather"),

                "temperature":
                    parse_number(
                        item.get("temp_avg")
                    ),

                "humidity":
                    parse_number(
                        item.get("rh_avg")
                    ),

                "wind_direction":
                    item.get("wind_from"),

                "wind_speed":
                    parse_number(
                        item.get("wind_speed")
                    ),

                "wind_gust":
                    parse_number(
                        item.get("wind_gust")
                    ),

                "wave_category":
                    item.get("wave_cat"),

                "wave_height":
                    parse_number(
                        item.get("wave_height")
                    ),

                "current_direction":
                    item.get("current_to"),

                "current_speed":
                    parse_number(
                        item.get("current_speed")
                    ),

                "issued_at":
                    issued_at,

                "valid_from":
                    valid_from,

                "valid_to":
                    valid_to,
            }

            data_utama.append(row)

    print("")
    print(
        "Total data utama:",
        len(data_utama)
    )

    # =====================================================
    # B. DATA GEMPA
    # =====================================================

    print("")
    print("====================================")
    print("EXTRACT DATA GEMPA")
    print("====================================")

    gempa_urls = {

        "latest":
            (
                f"{BASE_GEMPA_URL}"
                "autogempa.json"
            ),

        "m5":
            (
                f"{BASE_GEMPA_URL}"
                "gempaterkini.json"
            ),

        "felt":
            (
                f"{BASE_GEMPA_URL}"
                "gempadirasakan.json"
            ),
    }

    for source, url in gempa_urls.items():

        print(
            f"Mengambil gempa: {source}"
        )

        try:

            result = get_json(url)

        except Exception as error:

            print(
                f"GAGAL mengambil gempa "
                f"{source}: {error}"
            )

            continue

        if source == "latest":

            gempa = (
                result
                .get("Infogempa", {})
                .get("gempa")
            )

            if gempa:
                gempa_list = [gempa]
            else:
                gempa_list = []

        else:

            gempa_list = (
                result
                .get("Infogempa", {})
                .get(
                    "gempa",
                    []
                )
            )

        if not isinstance(
            gempa_list,
            list
        ):

            gempa_list = []

        for g in gempa_list:

            raw_datetime = (
                g.get("DateTime")
                or g.get("DateTimeUTC")
                or g.get("Datetime")
            )

            datetime_gempa = (
                convert_bmkg_datetime(
                    raw_datetime
                )
            )

            # ---------------------------------------------
            # PARSE LATITUDE
            # ---------------------------------------------

            latitude = None

            raw_lat = g.get("Lintang")

            if raw_lat:

                parts = str(
                    raw_lat
                ).split()

                try:

                    latitude = float(
                        parts[0]
                    )

                    if (
                        len(parts) > 1
                        and parts[1].upper()
                        == "LS"
                    ):

                        latitude *= -1

                except ValueError:

                    latitude = None

            # ---------------------------------------------
            # PARSE LONGITUDE
            # ---------------------------------------------

            longitude = None

            raw_lon = g.get("Bujur")

            if raw_lon:

                parts = str(
                    raw_lon
                ).split()

                try:

                    longitude = float(
                        parts[0]
                    )

                    if (
                        len(parts) > 1
                        and parts[1].upper()
                        in ["BB", "W"]
                    ):

                        longitude *= -1

                except ValueError:

                    longitude = None

            # ---------------------------------------------
            # PARSE KEDALAMAN
            # ---------------------------------------------

            depth = None

            raw_depth = g.get("Kedalaman")

            if raw_depth:

                try:

                    depth = float(
                        str(raw_depth)
                        .replace(
                            "km",
                            ""
                        )
                        .strip()
                    )

                except ValueError:

                    depth = None

            row = {

                "source":
                    source,

                "tanggal":
                    g.get("Tanggal"),

                "jam":
                    g.get("Jam"),

                "datetime_gempa":
                    datetime_gempa,

                "magnitude":
                    parse_number(
                        g.get("Magnitude")
                    ),

                "kedalaman_km":
                    depth,

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "wilayah":
                    g.get("Wilayah"),

                "potensi":
                    g.get("Potensi"),

                "dirasakan":
                    g.get("Dirasakan"),

                "shakemap":
                    g.get("Shakemap"),
            }

            data_gempa.append(row)

    print(
        "Total data gempa:",
        len(data_gempa)
    )

    # =====================================================
    # C. DATA CUACA PENDUKUNG
    # =====================================================

    print("")
    print("====================================")
    print("EXTRACT DATA CUACA PENDUKUNG")
    print("====================================")

    for location in WEATHER_LOCATIONS:

        adm4 = location["adm4"]

        location_name = (
            location["location_name"]
        )

        related_area = (
            location["related_area"]
        )

        print("")
        print(
            f"Mengambil cuaca: "
            f"{location_name}"
        )

        print(
            f"Wilayah terkait: "
            f"{related_area}"
        )

        print(
            f"ADM4: {adm4}"
        )

        try:

            weather_result = get_json(
                BASE_WEATHER_URL,
                params={
                    "adm4": adm4
                }
            )

        except Exception as error:

            print(
                f"GAGAL mengambil cuaca "
                f"{location_name}: {error}"
            )

            continue

        # -------------------------------------------------
        # STRUKTUR API BMKG
        # -------------------------------------------------

        data_list = weather_result.get(
            "data",
            []
        )

        if not isinstance(
            data_list,
            list
        ):

            print(
                "WARNING: format data cuaca "
                "tidak sesuai."
            )

            continue

        for data_item in data_list:

            if not isinstance(
                data_item,
                dict
            ):

                continue

            cuaca_groups = data_item.get(
                "cuaca",
                []
            )

            if not isinstance(
                cuaca_groups,
                list
            ):

                continue

            for group in cuaca_groups:

                if not isinstance(
                    group,
                    list
                ):

                    continue

                for item in group:

                    if not isinstance(
                        item,
                        dict
                    ):

                        continue

                    forecast_time = (
                        convert_bmkg_datetime(
                            item.get(
                                "local_datetime"
                            )
                        )
                    )

                    utc_datetime = (
                        convert_bmkg_datetime(
                            item.get(
                                "utc_datetime"
                            )
                        )
                    )

                    row = {

                        "adm4":
                            adm4,

                        "location_name":
                            location_name,

                        "related_area":
                            related_area,

                        "forecast_time":
                            forecast_time,

                        "utc_datetime":
                            utc_datetime,

                        "weather":
                            item.get(
                                "weather_desc"
                            ),

                        "temperature":
                            parse_number(
                                item.get("t")
                            ),

                        "humidity":
                            parse_number(
                                item.get("hu")
                            ),

                        "wind_speed":
                            parse_number(
                                item.get("ws")
                            ),

                        "visibility":
                            item.get(
                                "vs_text"
                            ),
                    }

                    data_cuaca.append(row)

    print("")
    print(
        "Total data cuaca:",
        len(data_cuaca)
    )

    # =====================================================
    # VALIDASI HASIL
    # =====================================================

    print("")
    print("====================================")
    print("RINGKASAN HASIL EXTRACT")
    print("====================================")

    print(
        "Data utama :",
        len(data_utama)
    )

    print(
        "Data gempa :",
        len(data_gempa)
    )

    print(
        "Data cuaca :",
        len(data_cuaca)
    )

    # =====================================================
    # SIMPAN HASIL TRANSFORM
    # =====================================================

    transformed = {

        "utama":
            data_utama,

        "gempa":
            data_gempa,

        "cuaca":
            data_cuaca,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            transformed,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("")
    print(
        "Hasil transform berhasil disimpan:"
    )

    print(
        OUTPUT_FILE
    )


# =========================================================
# 3. LOAD TO MYSQL
# =========================================================

def load_to_mysql():

    # =====================================================
    # BACA HASIL TRANSFORM
    # =====================================================

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        transformed = json.load(file)

    data_utama = transformed.get(
        "utama",
        []
    )

    data_gempa = transformed.get(
        "gempa",
        []
    )

    data_cuaca = transformed.get(
        "cuaca",
        []
    )

    hook = MySqlHook(
        mysql_conn_id="mysql-local"
    )

    # =====================================================
    # A. LOAD DATA UTAMA
    # =====================================================

    utama_sql = """

        INSERT INTO marine_data_utama (

            area_id,
            area_name,
            forecast_time,

            weather,
            temperature,
            humidity,

            wind_direction,
            wind_speed,
            wind_gust,

            wave_category,
            wave_height,

            current_direction,
            current_speed,

            issued_at,
            valid_from,
            valid_to
        )

        VALUES (

            %s, %s, %s,

            %s, %s, %s,

            %s, %s, %s,

            %s, %s,

            %s, %s,

            %s, %s, %s
        )

        ON DUPLICATE KEY UPDATE

            weather =
                VALUES(weather),

            temperature =
                VALUES(temperature),

            humidity =
                VALUES(humidity),

            wind_direction =
                VALUES(wind_direction),

            wind_speed =
                VALUES(wind_speed),

            wind_gust =
                VALUES(wind_gust),

            wave_category =
                VALUES(wave_category),

            wave_height =
                VALUES(wave_height),

            current_direction =
                VALUES(current_direction),

            current_speed =
                VALUES(current_speed),

            issued_at =
                VALUES(issued_at),

            valid_from =
                VALUES(valid_from),

            valid_to =
                VALUES(valid_to)

    """

    for row in data_utama:

        forecast_time = convert_bmkg_datetime(
            row.get("forecast_time")
        )

        issued_at = convert_bmkg_datetime(
            row.get("issued_at")
        )

        valid_from = convert_bmkg_datetime(
            row.get("valid_from")
        )

        valid_to = convert_bmkg_datetime(
            row.get("valid_to")
        )

        if forecast_time is None:

            print(
                "WARNING: forecast_time tidak valid."
            )

            print(
                row.get("forecast_time")
            )

            continue

        hook.run(
            utama_sql,
            parameters=(

                row["area_id"],
                row["area_name"],
                forecast_time,

                row["weather"],
                row["temperature"],
                row["humidity"],

                row["wind_direction"],
                row["wind_speed"],
                row["wind_gust"],

                row["wave_category"],
                row["wave_height"],

                row["current_direction"],
                row["current_speed"],

                issued_at,
                valid_from,
                valid_to,
            ),
        )

    print(
        f"{len(data_utama)} data "
        "diproses ke marine_data_utama."
    )

    # =====================================================
    # B. LOAD GEMPA
    # =====================================================

    gempa_sql = """

        INSERT INTO marine_data_gempa (

            source,
            tanggal,
            jam,
            datetime_gempa,

            magnitude,
            kedalaman_km,

            latitude,
            longitude,

            wilayah,
            potensi,
            dirasakan,
            shakemap
        )

        VALUES (

            %s, %s, %s, %s,

            %s, %s,

            %s, %s,

            %s, %s, %s, %s
        )

        ON DUPLICATE KEY UPDATE

            source =
                VALUES(source),

            potensi =
                VALUES(potensi),

            dirasakan =
                VALUES(dirasakan),

            shakemap =
                VALUES(shakemap)

    """

    for row in data_gempa:

        datetime_gempa = convert_bmkg_datetime(
            row.get("datetime_gempa")
        )

        hook.run(
            gempa_sql,
            parameters=(

                row["source"],
                row["tanggal"],
                row["jam"],
                datetime_gempa,

                row["magnitude"],
                row["kedalaman_km"],

                row["latitude"],
                row["longitude"],

                row["wilayah"],
                row["potensi"],
                row["dirasakan"],
                row["shakemap"],
            ),
        )

    print(
        f"{len(data_gempa)} data "
        "diproses ke marine_data_gempa."
    )

    # =====================================================
    # C. LOAD CUACA
    # =====================================================

    cuaca_sql = """

        INSERT INTO marine_data_cuaca (

            adm4,
            location_name,
            related_area,

            forecast_time,
            utc_datetime,

            weather,
            temperature,
            humidity,
            wind_speed,
            visibility
        )

        VALUES (

            %s, %s, %s,

            %s, %s,

            %s, %s, %s, %s, %s
        )

        ON DUPLICATE KEY UPDATE

            location_name =
                VALUES(location_name),

            related_area =
                VALUES(related_area),

            utc_datetime =
                VALUES(utc_datetime),

            weather =
                VALUES(weather),

            temperature =
                VALUES(temperature),

            humidity =
                VALUES(humidity),

            wind_speed =
                VALUES(wind_speed),

            visibility =
                VALUES(visibility)

    """

    for row in data_cuaca:

        local_time = convert_bmkg_datetime(
            row.get("forecast_time")
        )

        utc_time = convert_bmkg_datetime(
            row.get("utc_datetime")
        )

        hook.run(
            cuaca_sql,
            parameters=(

                row["adm4"],
                row["location_name"],
                row["related_area"],

                local_time,
                utc_time,

                row["weather"],
                row["temperature"],
                row["humidity"],
                row["wind_speed"],
                row["visibility"],
            ),
        )

    print(
        f"{len(data_cuaca)} data "
        "diproses ke marine_data_cuaca."
    )

    # =====================================================
    # SELESAI
    # =====================================================

    print("")
    print("====================================")
    print("LOAD SELESAI")
    print("====================================")

    print(
        "Data utama :",
        len(data_utama)
    )

    print(
        "Data gempa :",
        len(data_gempa)
    )

    print(
        "Data cuaca :",
        len(data_cuaca)
    )

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

    # Jalan setiap 1 jam
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