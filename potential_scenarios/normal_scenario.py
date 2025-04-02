import pandas as pd
import numpy as np
from scipy.stats import norm
from models.qn2_inventory_optimization import get_quarterly_reorder_point, get_quarterly_eoq


def apply_naive_inventory_strategy(demand_df, stock_df):
    """
    Naive inventory strategy with dynamic stock depletion, adjusted for realistic business conditions.

    Adjustments:
    - Reorder when stock < 80% of last quarter’s demand (instead of 50%).
    - Maintain safety stock at 50% of last quarter’s demand.
    - Order 110% of last quarter’s demand when restocking.
    - Track rolling stock levels and unmet demand.
    """
    # Sort data
    demand_df = demand_df.sort_values(by=["cluster_label", "year_quarter"])

    # Get last quarter's demand per cluster
    demand_df["last_quarter_demand"] = demand_df.groupby("cluster_label")["predicted_demand"].shift(1)

    # Adjust reorder point: Trigger reorder if stock falls below 80% of last quarter’s demand
    demand_df["naive_reorder_point"] = demand_df["last_quarter_demand"] * 0.8

    # Adjust safety stock: Set safety stock at 20% of last quarter's demand
    demand_df["naive_safety_stock"] = demand_df["last_quarter_demand"] * 0.2

    # Adjust order quantity: Order 110% of last quarter's demand when restocking
    demand_df["naive_order_qty"] = demand_df["last_quarter_demand"] * 1.1

    # Merge with stock data
    stock_df = stock_df[["cluster_label", "stock_quantity"]]
    demand_df = demand_df.merge(stock_df, on="cluster_label", how="left")

    # Determine if restocking is needed (based on the adjusted reorder point)
    demand_df["naive_restock"] = demand_df["stock_quantity"] < demand_df["naive_reorder_point"]

    # Set order quantity to naive_order_qty only if restocking is needed
    demand_df["naive_order_qty"] = np.where(demand_df["naive_restock"], demand_df["naive_order_qty"], 0)

    # Update rolling stock levels over time
    demand_df["rolling_stock"] = demand_df.groupby("cluster_label")["stock_quantity"].shift(1)
    demand_df.loc[demand_df["year_quarter"] == demand_df["year_quarter"].min(), "rolling_stock"] = demand_df[
        "stock_quantity"]

    # Update rolling stock: subtract demand, add order
    demand_df["rolling_stock"] = demand_df["rolling_stock"] - demand_df["predicted_demand"] + demand_df[
        "naive_order_qty"]

    # Track unmet demand if stock goes negative
    demand_df["unmet_demand"] = demand_df["rolling_stock"].apply(lambda x: abs(x) if x < 0 else 0)

    return demand_df.reset_index(drop=True)



def get_quarterly_restock(df_1, df_2, z_score):
    """
    Computes restocking decisions per quarter, with rolling stock updates and stockout tracking.

    - Orders when stock < reorder point.
    - Uses EOQ to determine optimal order quantity.
    - Tracks rolling stock depletion.
    - Tracks stockouts (unmet demand).
    """

    # Get reorder points and EOQ
    reorder_point_df = get_quarterly_reorder_point(df_1, df_2, z_score)[
        ['cluster_label', 'year_quarter', 'reorder_point']]
    eoq_df = get_quarterly_eoq(df_1, df_2)[['cluster_label', 'year_quarter', 'optimal_qty']]
    stock_df = df_2[['cluster_label', 'stock_quantity']]

    # Merge all data
    to_restock_df = pd.merge(reorder_point_df, eoq_df, on=['cluster_label', 'year_quarter'])
    to_restock_df = pd.merge(to_restock_df, stock_df, on='cluster_label')

    # Add restock flag
    to_restock_df['to_restock'] = to_restock_df.apply(
        lambda row: 1 if (row['stock_quantity'] <= row['reorder_point']) and
                         (row['reorder_point'] > 0) and
                         (row['optimal_qty'] > 0) else 0, axis=1)

    # Rename for consistency
    to_restock_df = to_restock_df.rename(columns={'optimal_qty': 'order_qty'})

    # Implement rolling stock updates per quarter
    to_restock_df["rolling_stock"] = to_restock_df.groupby("cluster_label")["stock_quantity"].shift(1)

    # First quarter keeps initial stock
    to_restock_df.loc[to_restock_df["year_quarter"] == to_restock_df["year_quarter"].min(), "rolling_stock"] = \
    to_restock_df["stock_quantity"]

    # Update rolling stock (subtract demand, add new orders)
    to_restock_df["rolling_stock"] = to_restock_df["rolling_stock"] - df_1["predicted_demand"] + to_restock_df[
        "order_qty"]

    # Track unmet demand (if stock goes negative)
    to_restock_df["unmet_demand"] = to_restock_df["rolling_stock"].apply(lambda x: abs(x) if x < 0 else 0)

    return to_restock_df.reset_index(drop=True)



def compare_inventory_models(optimized_df, baseline_df, inventory_df):
    """
    Compare inventory performance between the optimized inventory algorithm and the baseline (naive) strategy.

    Parameters:
        optimized_df (DataFrame): Result DataFrame from the optimized inventory algorithm.
        baseline_df (DataFrame): Result DataFrame from the baseline (naive) strategy.
        inventory_df (DataFrame): Stock DataFrame containing cost data ('cluster_label', 'order_cost', 'holding_cost').

    Returns:
        comparison_df (DataFrame): A summary DataFrame comparing key performance metrics:
                                   - Total Unmet Demand
                                   - Stockout Rate (%)
                                   - Service Level (%)
                                   - Total Ordering Cost
                                   - Average Holding Cost
    """
    # Rename baseline columns to match our optimized model for consistency
    baseline_df = baseline_df.rename(columns={"naive_restock": "to_restock", "naive_order_qty": "order_qty"})

    # Extract cost information from the inventory DataFrame
    cost_df = inventory_df[['cluster_label', 'order_cost', 'holding_cost']]

    # Merge cost info into both result DataFrames
    optimized_df = optimized_df.merge(cost_df, on="cluster_label", how="left")
    baseline_df = baseline_df.merge(cost_df, on="cluster_label", how="left")

    # For the Optimized Algorithm
    total_unmet_optimized = optimized_df["unmet_demand"].sum()
    stockout_rate_optimized = (optimized_df[optimized_df["unmet_demand"] > 0].shape[0] / optimized_df.shape[0]) * 100
    service_level_optimized = 100 - stockout_rate_optimized
    total_ordering_cost_optimized = (optimized_df["order_qty"] * optimized_df["order_cost"]).sum()

    # Use rolling_stock but only count positive stock for holding cost calculation
    positive_rolling_stock_optimized = optimized_df["rolling_stock"].where(optimized_df["rolling_stock"] > 0, 0)
    avg_holding_cost_optimized = (positive_rolling_stock_optimized * optimized_df["holding_cost"]).sum() / max(
        len(optimized_df), 1)

    # For the Baseline (Naive) Strategy
    total_unmet_baseline = baseline_df["unmet_demand"].sum()
    stockout_rate_baseline = (baseline_df[baseline_df["unmet_demand"] > 0].shape[0] / baseline_df.shape[0]) * 100
    service_level_baseline = 100 - stockout_rate_baseline
    total_ordering_cost_baseline = (baseline_df["order_qty"] * baseline_df["order_cost"]).sum()
    positive_rolling_stock_baseline = baseline_df["rolling_stock"].where(baseline_df["rolling_stock"] > 0, 0)
    avg_holding_cost_baseline = (positive_rolling_stock_baseline * baseline_df["holding_cost"]).sum() / max(
        len(baseline_df), 1)

    # Create a summary comparison DataFrame
    comparison_df = pd.DataFrame({
        "Model": ["Our Algorithm", "Naive Strategy"],
        "Total Unmet Demand": [total_unmet_optimized, total_unmet_baseline],
        "Stockout Rate (%)": [round(stockout_rate_optimized, 2), round(stockout_rate_baseline, 2)],
        "Service Level (%)": [round(service_level_optimized, 2), round(service_level_baseline, 2)],
        "Total Ordering Cost": [round(total_ordering_cost_optimized, 2), round(total_ordering_cost_baseline, 2)],
        "Avg Holding Cost": [round(avg_holding_cost_optimized, 2), round(avg_holding_cost_baseline, 2)]
    })

    return comparison_df


# Load datasets
demand_df = pd.read_csv("../dataset/simulated_demand.csv")
stock_df = pd.read_csv("../dataset/simulated_stock.csv")

# Convert date column to datetime
demand_df['date'] = pd.to_datetime(demand_df['date'], format="%Y-%m-%d")

# Extract year and quarter from date
demand_df['year_quarter'] = demand_df['date'].dt.to_period("Q")

demand_df['moving_avg_demand'] = demand_df.groupby(by=['cluster_label'])['predicted_demand'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())

# Apply naive strategy
naive_results_df = apply_naive_inventory_strategy(demand_df, stock_df)

print(naive_results_df.head())

# Save results if needed
# naive_results_df.to_csv("../dataset/naive_inventory_results.csv", index=False)

# Apply our algo
service_level = 0.95
z_score = norm.ppf(service_level)

algo_result_df= get_quarterly_restock(demand_df, stock_df, z_score)

print(algo_result_df.head())

# Save results if needed
# algo_result_df.to_csv("../dataset/algo_result.csv", index=False)

# Make comparison
comparison = compare_inventory_models(algo_result_df, naive_results_df, stock_df)

print(comparison)

# Save results
comparison.to_csv("../dataset/comparison_summary.csv", index=False)

