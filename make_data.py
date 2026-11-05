"""Generate the fictional sample data used by the dashboard (data/sales.csv).

One row per month x region x product, Jan 2024 - Dec 2025.
Run once: python make_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

PRODUCTS = [
    # product, category, unit price (NOK), margin
    ("Trail Pro Shell Jacket", "Jackets", 2490, 0.47),
    ("Vidde Down Parka", "Jackets", 3990, 0.49),
    ("Breeze Wind Jacket", "Jackets", 1290, 0.42),
    ("Fjell GTX Hiking Boot", "Footwear", 2190, 0.40),
    ("Sti Trail Runner", "Footwear", 1490, 0.36),
    ("Vinter Insulated Boot", "Footwear", 1890, 0.38),
    ("Tind 40L Backpack", "Backpacks", 1290, 0.47),
    ("Dag 22L Daypack", "Backpacks", 690, 0.45),
    ("Ekspedisjon 65L Pack", "Backpacks", 2290, 0.44),
    ("Lofoten 2-person Tent", "Camping gear", 4490, 0.33),
    ("Polar Sleeping Bag", "Camping gear", 1990, 0.36),
    ("Leir Camping Stove", "Camping gear", 790, 0.38),
    ("Merino Wool Beanie", "Accessories", 299, 0.55),
    ("Trekking Poles (pair)", "Accessories", 599, 0.50),
    ("Thermal Bottle 0.75 L", "Accessories", 349, 0.52),
]
BASE_UNITS = [38, 16, 30, 30, 34, 22, 40, 52, 14, 9, 20, 34, 120, 44, 70]
REGIONS = {"Oslo": 0.29, "Vestland": 0.19, "Rogaland": 0.17, "Trøndelag": 0.13, "Online, rest of Norway": 0.22}
SEASON = {  # monthly demand index per category
    "Jackets":      [0.9, 0.7, 0.7, 0.7, 0.6, 0.5, 0.5, 0.7, 1.1, 1.4, 1.6, 1.9],
    "Footwear":     [0.8, 0.7, 0.9, 1.1, 1.2, 1.2, 1.1, 1.0, 1.0, 1.0, 1.1, 1.3],
    "Backpacks":    [0.6, 0.6, 0.8, 1.0, 1.3, 1.5, 1.5, 1.3, 1.0, 0.8, 0.8, 1.1],
    "Camping gear": [0.4, 0.4, 0.6, 0.9, 1.4, 1.8, 1.9, 1.4, 0.8, 0.5, 0.5, 0.8],
    "Accessories":  [1.0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.9, 1.1, 1.4, 2.2],
}

rows = []
for month in pd.date_range("2024-01-01", "2025-12-01", freq="MS"):
    growth = 1.0 if month.year == 2024 else 1.09
    for (name, cat, price, margin), base in zip(PRODUCTS, BASE_UNITS):
        for region, share in REGIONS.items():
            mean = base * 5 * share * SEASON[cat][month.month - 1] * growth
            units = int(rng.poisson(max(mean, 0.5)))
            p = price * (1.02 if month.year == 2025 else 1.0)
            revenue = units * p * rng.normal(0.97, 0.015)  # small average discount
            rows.append({
                "month": month.strftime("%Y-%m-%d"),
                "region": region,
                "category": cat,
                "product": name,
                "units": units,
                "revenue": round(revenue, 2),
                "gross_profit": round(revenue * margin * rng.normal(1, 0.02), 2),
            })

df = pd.DataFrame(rows)
df.to_csv("data/sales.csv", index=False)
print(f"{len(df)} rows written to data/sales.csv")
