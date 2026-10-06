import pandas as pd

data = [
    ["P.AF.01", "Selat Labengki", -3.46, 122.43],
    ["P.AF.02", "Laut Labengki", -3.35, 122.55],
    ["P.AF.04", "Teluk Kendari - Moramo", -4.00, 122.65],
    ["P.AF.05", "Selat Wawoni", -4.20, 122.95],
    ["P.AF.13", "Perairan Buton", -5.00, 122.80],
    ["P.AF.14", "Teluk Bone Barat Kolaka Utara", -3.50, 121.80],
    ["P.AF.19", "Laut Banda Timur Wakatobi", -5.30, 123.80],
]

df = pd.DataFrame(
    data,
    columns=["area_id", "area_name", "latitude", "longitude"]
)

print(df)