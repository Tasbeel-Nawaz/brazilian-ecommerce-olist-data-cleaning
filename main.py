import pandas as pd
from pathlib import Path

# 1. Create output folders
Path("Data/Cleaned").mkdir(parents=True, exist_ok=True)
Path("reports").mkdir(parents=True, exist_ok=True)

# 2. Read raw datasets
raw = Path("Data/Raw")

orders = pd.read_csv(raw / "olist_orders_dataset.csv")
customers = pd.read_csv(raw / "olist_customers_dataset.csv")
items = pd.read_csv(raw / "olist_order_items_dataset.csv")
products = pd.read_csv(raw / "olist_products_dataset.csv")
translation = pd.read_csv(raw / "product_category_name_translation.csv")
sellers = pd.read_csv(raw / "olist_sellers_dataset.csv")
payments = pd.read_csv(raw / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(raw / "olist_order_reviews_dataset.csv")
geolocation = pd.read_csv(raw / "olist_geolocation_dataset.csv")

# 3. Initial data quality check
print("\n--- INITIAL DATA QUALITY CHECK ---")
print("Orders shape:", orders.shape)
print("\nMissing values by column:")
print(orders.isnull().sum())
print("\nTotal missing cells:", orders.isnull().sum().sum())
print("Duplicate rows:", orders.duplicated().sum())

# 4. Convert order date columns to datetime
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

# Keep actual delivery dates unchanged.
# Missing actual dates should not be replaced with estimated dates.

# Save cleaned orders
orders.to_csv("Data/Cleaned/olist_orders_dataset.csv", index=False)
print("\nCleaned orders file saved.")

# 5. Aggregate geolocation to prevent duplicate zip-code matches
print("\nProcessing geolocation...")

geo_agg = (
    geolocation
    .groupby("geolocation_zip_code_prefix")[
        ["geolocation_lat", "geolocation_lng"]
    ]
    .mean()
    .reset_index()
)

# 6. Translate product categories
products_translated = pd.merge(
    products,
    translation,
    on="product_category_name",
    how="left"
)

products_translated["product_category_name_english"] = (
    products_translated["product_category_name_english"]
    .fillna("Unknown")
)

# 7. Merge all datasets
print("\nMerging datasets...")

master_df = pd.merge(
    orders, customers, on="customer_id", how="left"
)

master_df = pd.merge(
    master_df,
    geo_agg,
    left_on="customer_zip_code_prefix",
    right_on="geolocation_zip_code_prefix",
    how="left"
)

master_df = master_df.rename(
    columns={
        "geolocation_lat": "customer_lat",
        "geolocation_lng": "customer_lng"
    }
)

master_df = master_df.drop(
    columns=["geolocation_zip_code_prefix"],
    errors="ignore"
)

master_df = pd.merge(master_df, items, on="order_id", how="left")
master_df = pd.merge(
    master_df, products_translated, on="product_id", how="left"
)
master_df = pd.merge(master_df, sellers, on="seller_id", how="left")
master_df = pd.merge(master_df, payments, on="order_id", how="left")
master_df = pd.merge(master_df, reviews, on="order_id", how="left")

# 8. Final data quality report
print("\n--- FINAL DATA QUALITY CHECK ---")
print("Master dataset shape:", master_df.shape)
print("Total missing cells:", master_df.isnull().sum().sum())
print("Duplicate rows:", master_df.duplicated().sum())
print(
    "Rows missing order_item_id:",
    master_df["order_item_id"].isnull().sum()
)

# 9. Save master dataset
output_file = "Data/Cleaned/ultimate_olist_master_dataset_with_geo.csv"
master_df.to_csv(output_file, index=False)

# 10. Save quality summary
summary = pd.DataFrame({
    "Metric": [
        "Total Rows",
        "Total Columns",
        "Total Missing Cells",
        "Duplicate Rows",
        "Rows Missing order_item_id"
    ],
    "Value": [
        len(master_df),
        len(master_df.columns),
        int(master_df.isnull().sum().sum()),
        int(master_df.duplicated().sum()),
        int(master_df["order_item_id"].isnull().sum())
    ]
})

summary.to_csv("reports/data_quality_summary.csv", index=False)

print("\nMaster dataset saved successfully!")
print("Quality report saved successfully!")
print("Pipeline completed.")