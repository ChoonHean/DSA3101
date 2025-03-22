import pandas as pd
import numpy as np
from scipy.stats import norm

# Load dataset
demand_df = pd.read_csv("../dataset/modified_predicted_demand.csv")
stock_df = pd.read_csv("../dataset/generated_cluster_stock.csv")

# Convert date column to datetime
demand_df['date'] = pd.to_datetime(demand_df['date'], format="%Y-%m-%d")

# Extract year and quarter from date
demand_df['year_quarter'] = demand_df['date'].dt.to_period("Q")

# Compute standard deviation of demand
std_dev_demand = demand_df["predicted_demand"].std()

# Set desired service level (e.g. 95% confidence)
service_level = 0.95
z_score = norm.ppf(service_level)

print(f"Standard Deviation of Predicted Sales: {std_dev_demand:.2f}")
print(f"Z-score for {service_level*100}% service level: {z_score:.3f}")

# Calculate quarterly safety stock
def get_quarterly_safety_stock(df_1, df_2, z_score):
    df_2 = df_2[['cluster_label', 'lead_time_months']]

    # Group by cluster_label and quarter, then compute standard deviation
    safety_stock_df = df_1.groupby(['cluster_label', 'year_quarter'])['moving_avg_demand'].std().reset_index()
    safety_stock_df = pd.merge(safety_stock_df, df_2, on='cluster_label')
    safety_stock_df = safety_stock_df.rename(columns={'moving_avg_demand': 'quarterly_pd_std'})

    safety_stock_df['quarterly_pd_std'] = safety_stock_df['quarterly_pd_std'].fillna(1.0)

    # Convert lead time to quarters (round up)
    safety_stock_df['lead_time_quarters'] = (safety_stock_df['lead_time_months'] / 3).apply(np.ceil)

    # Compute Quarterly Safety Stock
    safety_stock_df['quarterly_safety_stock'] = np.maximum(
        z_score * safety_stock_df['quarterly_pd_std'] * np.sqrt(np.maximum(safety_stock_df['lead_time_quarters'], 1)),
        5
    )

    return safety_stock_df.drop(columns=['lead_time_quarters'])

# Calculate quarterly reorder point
def get_quarterly_reorder_point(df_1, df_2, z_score):
    # Compute average quarterly demand per cluster
    reorder_df = df_1.groupby(['cluster_label', 'year_quarter'])['moving_avg_demand'].mean().reset_index()
    reorder_df = reorder_df.rename(columns={'moving_avg_demand': 'quarterly_avg_pd'})
    reorder_df['quarterly_avg_pd'] = reorder_df['quarterly_avg_pd'].fillna(0)

    # Get safety stock for each cluster and quarter
    safety_stock_df = get_quarterly_safety_stock(df_1, df_2, z_score).drop(columns=['quarterly_pd_std'])
    reorder_df = pd.merge(reorder_df, safety_stock_df, on=['cluster_label', 'year_quarter'], how="outer")
    reorder_df['quarterly_safety_stock'] = reorder_df['quarterly_safety_stock'].fillna(0)

    # Create a lead time dataframe: one row per cluster
    lead_time_df = df_2[['cluster_label', 'lead_time_months']].drop_duplicates()
    # Convert lead time from months to quarters (round up)
    lead_time_df['lead_time_quarters'] = np.ceil(lead_time_df['lead_time_months'] / 3)
    # Merge this info into reorder_df based on cluster_label
    reorder_df = pd.merge(reorder_df, lead_time_df[['cluster_label', 'lead_time_quarters']], on='cluster_label', how='left')
    reorder_df['lead_time_quarters'] = reorder_df['lead_time_quarters'].fillna(1)

    # Reorder Point = (Quarterly Avg Demand × Lead Time in Quarters) + Safety Stock
    reorder_df['reorder_point'] = (reorder_df['quarterly_avg_pd'] * reorder_df['lead_time_quarters']) + reorder_df['quarterly_safety_stock']

    return reorder_df


# Calculate quarterly EOQ
def get_quarterly_eoq(df_1, df_2):
    eoq_df = df_1.groupby(['cluster_label', 'year_quarter'])['moving_avg_demand'].mean().reset_index()
    eoq_df = eoq_df.rename(columns={'moving_avg_demand': "quarterly_avg_demand"})

    df_2 = df_2[['cluster_label', 'order_cost', 'holding_cost']]
    eoq_df = pd.merge(eoq_df, df_2, on='cluster_label')

    # Calculate EOQ: Economic Order Quantity per Quarter
    eoq_df['optimal_qty'] = np.round(np.sqrt((2 * eoq_df['quarterly_avg_demand'] * eoq_df['order_cost']) / eoq_df['holding_cost'])).astype(int)
    eoq_df = eoq_df.drop(columns=['order_cost', 'holding_cost'])

    return eoq_df

# Find clusters that teed testocking
def get_quarterly_restock(df_1, df_2, z_score):
    reorder_point_df = get_quarterly_reorder_point(df_1, df_2, z_score)[['cluster_label', 'year_quarter', 'reorder_point']]
    eoq_df = get_quarterly_eoq(df_1, df_2)[['cluster_label', 'year_quarter', 'optimal_qty']]
    stock_df = df_2[['cluster_label', 'stock_quantity']]

    to_restock_df = pd.merge(reorder_point_df, eoq_df, on=['cluster_label', 'year_quarter'])
    to_restock_df = pd.merge(to_restock_df, stock_df, on='cluster_label')

    # Identify which clusters need restocking
    to_restock_df['to_restock'] = to_restock_df.apply(
        lambda row: 1 if (row['stock_quantity'] <= row['reorder_point']) and (row['reorder_point'] > 0) and (
                    row['optimal_qty'] > 0) else 0, axis=1)

    # Filter for clusters that need restocking
    to_restock_df = to_restock_df[to_restock_df['to_restock'] == 1].reset_index(drop=True)

    return to_restock_df[['cluster_label', 'year_quarter', 'to_restock', 'optimal_qty']]

# Save final restock list
result = get_quarterly_restock(demand_df, stock_df, z_score)
result.to_csv("../dataset/quarterly_restock_list.csv", index=False)

