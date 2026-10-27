import pandas as pd

df = pd.read_csv('Data/Cleaned/ultimate_olist_master_dataset_with_geo.csv')
print("\n--- INITIAL DATA QUALITY CHECK ---")
print("Shape:", df.shape)
print("\nData types:")
print(df.dtypes)
print("\nMissing values by column:")
print(df.isnull().sum())
print("\nTotal missing cells:", df.isnull().sum().sum())
print("\nDuplicate occurrences:", df.duplicated().sum())


# 1.olist_orders_dataset.csv
orders_df = pd.read_csv("Data/Cleaned/olist_orders_dataset.csv")
# 2. INITIAL DATA QUALITY CHECK
print("\n--- INITIAL DATA QUALITY CHECK ---")
print("Shape:", orders_df.shape)
print("\nData types:")
print(orders_df.dtypes)
print("\nMissing values by column:")
print(orders_df.isnull().sum())
print("\nTotal missing cells:", orders_df.isnull().sum().sum())
print("\nDuplicate occurrences:", orders_df.duplicated().sum())
print("\nQuantity and Price summary:")
missing_dates = orders_df[orders_df["order_delivered_customer_date"].isnull()]
print(missing_dates["order_status"].value_counts())
condition = (orders_df['order_status'] == 'delivered') & (orders_df['order_delivered_customer_date'].isnull())
print("after Number of missing delivered dates for 'delivered' orders:", condition.sum())
orders_df.loc[condition, 'order_delivered_customer_date'] = orders_df.loc[condition, 'order_estimated_delivery_date']
orders_df.to_csv("reports/olist_orders_dataset.csv", index=False)
print("File successfully saved!")
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_approved_at'] = pd.to_datetime(orders_df['order_approved_at'])
orders_df['order_delivered_carrier_date'] = pd.to_datetime(orders_df['order_delivered_carrier_date'])
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])
orders_df['order_estimated_delivery_date'] = pd.to_datetime(orders_df['order_estimated_delivery_date'])
orders_df.to_csv("Data/Cleaned/olist_orders_datasets.csv", index=False)

#2 file merging
customers = pd.read_csv('reports/olist_customers_dataset.csv')
items = pd.read_csv('reports/olist_order_items_dataset.csv')
products = pd.read_csv('reports/olist_products_dataset.csv')
translation = pd.read_csv('reports/product_category_name_translation.csv')
sellers = pd.read_csv('reports/olist_sellers_dataset.csv')
payments = pd.read_csv('reports/olist_order_payments_dataset.csv')
reviews = pd.read_csv('reports/olist_order_reviews_dataset.csv')
geolocation = pd.read_csv('reports/olist_geolocation_dataset.csv')

print("Preprocessing Geolocation to avoid row explosion...")
geo_agg = geolocation.groupby('geolocation_zip_code_prefix')[['geolocation_lat', 'geolocation_lng']].mean().reset_index()
products_translated = pd.merge(products, translation, on='product_category_name', how='left')
products_translated['product_category_name_english'] = products_translated['product_category_name_english'].fillna('Unknown')
print("Starting the ultimate merging process...")
master_df = pd.merge(orders, customers, on='customer_id', how='left')
master_df = pd.merge(master_df, geo_agg, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')
master_df.rename(columns={'geolocation_lat': 'customer_lat', 'geolocation_lng': 'customer_lng'}, inplace=True)
master_df.drop(columns=['geolocation_zip_code_prefix'], inplace=True, errors='ignore')
master_df = pd.merge(master_df, items, on='order_id', how='left')
master_df = pd.merge(master_df, products_translated, on='product_id', how='left')
master_df = pd.merge(master_df, sellers, on='seller_id', how='left')
master_df = pd.merge(master_df, payments, on='order_id', how='left')
master_df = pd.merge(master_df, reviews, on='order_id', how='left')
print("All Tables Merged Successfully!")
print("Ultimate Master Table Shape:", master_df.shape)
master_df.to_csv('Data/Cleaned/ultimate_olist_master_dataset_with_geo.csv', index=False)
print("Complete master dataset with geolocation saved successfully!")


#3 Duplicated check
df = pd.read_csv('Data/Cleaned/ultimate_olist_master_dataset_with_geo.csv')
print(df.columns[df.T.duplicated()].tolist())
dup = df[df.duplicated(keep=False)]
print(dup)

# 4 empty product id remove
df = pd.read_csv('Data/Cleaned/ultimate_olist_master_dataset_with_geo.csv')
print(f"Total rows in dataset: {len(df)}")
df = df.dropna(subset=['order_item_id'])
print(f"Cleaning ke baad total rows: {len(df)}")
# Updated file ko dobara save kar dein
df.to_csv('Data/Cleaned/ultimate_olist_master_dataset_with_geo.csv', index=False)
print("Dataset bilkul clean ho gaya hai!")
print(f"Total rows in dataset: {len(df)}")