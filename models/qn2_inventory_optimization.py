import pandas as pd
import numpy as np
from scipy.stats import norm

# Load dataset
demand_df = pd.read_csv("../dataset/next_year_demand.csv")

# Transform demand_df
def convert_to_date(year, quarter):
    """
    Convert year and quarter into a real date.
    The date corresponds to the first day of the quarter.
    """
    # Define mapping of quarter to the first month
    quarter_to_month = {1: "01", 2: "04", 3: "07", 4: "10"}

    # Format the date as YYYY-MM-DD
    return pd.to_datetime(f"{year}-{quarter_to_month[quarter]}-01", format="%Y-%m-%d")


demand_df["date"] = demand_df.apply(lambda row: convert_to_date(row["year"], row["quarter"]), axis=1)
demand_df = demand_df.drop(columns=["year", "quarter"])
demand_df['moving_avg_demand'] = demand_df.groupby(by=['cluster_label'])['predicted_demand'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())

demand_df['date'] = pd.to_datetime(demand_df['date'], format="%Y-%m-%d")
demand_df['year_quarter'] = demand_df['date'].dt.to_period("Q")
std_dev_demand = demand_df["predicted_demand"].std()

# Set desired service level (e.g. 95% confidence)
service_level = 0.95
z_score = norm.ppf(service_level)

# Create stock_df
stock_df = demand_df.copy()
stock_df = stock_df.groupby("cluster_label").agg({
    "predicted_demand": "sum"
}).reset_index()

np.random.seed(42)  # Set seed for reproducibility
stock_df["stock_quantity"] = stock_df["predicted_demand"] * 0.5
stock_df["lead_time_months"] = np.random.uniform(0.1, 3, size=len(stock_df)).round(2)
stock_df["order_cost"] = np.random.randint(20, 80, size=len(stock_df))
stock_df["holding_cost"] = np.random.randint(2, 10, size=len(stock_df))
stock_df["last_restocked"] = "01/07/2023"

# Select final columns (without category column)
stock_df = stock_df[[
    "cluster_label", "stock_quantity",
    "lead_time_months", "order_cost", "holding_cost", "last_restocked"
]]


def get_quarterly_safety_stock(df_1, df_2, z_score):
    """
        Calculate quarterly safety stock for each cluster using standard deviation
        of moving average demand and lead time.

        Parameters:
            df_1 (pd.DataFrame): Demand dataframe
            df_2 (pd.DataFrame): Stock dataframe
            z_score (float): Z-score corresponding to the desired service level.

        Returns:
            pd.DataFrame: Quarterly safety stock values per cluster and quarter.
    """
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


def get_quarterly_reorder_point(df_1, df_2, z_score):
    """
        Calculate reorder point for each cluster and quarter using:
        Reorder Point = (Avg Demand × Lead Time) + Safety Stock

        Parameters:
            df_1 (pd.DataFrame): Demand dataframe
            df_2 (pd.DataFrame): Stock dataframe
            z_score (float): Z-score for service level.

        Returns:
            pd.DataFrame: Reorder point per cluster and quarter.
    """
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

    # Calculate reorder point
    reorder_df['reorder_point'] = (reorder_df['quarterly_avg_pd'] * reorder_df['lead_time_quarters']) + reorder_df['quarterly_safety_stock']

    return reorder_df


def get_quarterly_eoq(df_1, df_2):
    """
        Calculate EOQ (Economic Order Quantity) for each cluster per quarter.

        Parameters:
            df_1 (pd.DataFrame): Demand dataframe
            df_2 (pd.DataFrame): Stock dataframe

        Returns:
            pd.DataFrame: EOQ values per cluster and quarter.
    """
    eoq_df = df_1.groupby(['cluster_label', 'year_quarter'])['moving_avg_demand'].mean().reset_index()
    eoq_df = eoq_df.rename(columns={'moving_avg_demand': "quarterly_avg_demand"})

    df_2 = df_2[['cluster_label', 'order_cost', 'holding_cost']]
    eoq_df = pd.merge(eoq_df, df_2, on='cluster_label')

    # Calculate EOQ
    eoq_df['optimal_qty'] = np.round(np.sqrt((2 * eoq_df['quarterly_avg_demand'] * eoq_df['order_cost']) / eoq_df['holding_cost'])).astype(int)
    eoq_df = eoq_df.drop(columns=['order_cost', 'holding_cost'])

    return eoq_df


def get_quarterly_restock(df_1, df_2, z_score):
    """
        Determine which clusters need restocking for each quarter.

        Parameters:
            df_1 (pd.DataFrame): Demand dataframe.
            df_2 (pd.DataFrame): Stock dataframe.
            z_score (float): Z-score for service level.

        Returns:
            pd.DataFrame: Clusters and quarters where restocking is needed, along with optimal quantity.
    """
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

