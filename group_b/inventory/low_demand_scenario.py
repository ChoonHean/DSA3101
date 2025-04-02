import pandas as pd
from scipy.stats import norm
from normal_scenario import apply_naive_inventory_strategy, compare_inventory_models, get_quarterly_restock

# Load datasets
demand_df = pd.read_csv("data/simulated_demand.csv")
stock_df = pd.read_csv("data/simulated_stock.csv")

# Make demand and stock 0.1 times smaller
demand_df["predicted_demand"] = (demand_df["predicted_demand"] * 0.1).round().astype(int)
stock_df["stock_quantity"] = (stock_df["stock_quantity"] * 0.1).round().astype(int)

# Convert date column to datetime
demand_df['date'] = pd.to_datetime(demand_df['date'], format="%Y-%m-%d")

# Extract year and quarter from date
demand_df['year_quarter'] = demand_df['date'].dt.to_period("Q")

demand_df['moving_avg_demand'] = demand_df.groupby(by=['cluster_label'])['predicted_demand'].transform(
    lambda x: x.rolling(window=10, min_periods=1).mean())

# Apply naive strategy
naive_results_df = apply_naive_inventory_strategy(demand_df, stock_df)

print(naive_results_df.head())

# Save results if needed
# naive_results_df.to_csv("../raw_data/low_demand_naive_inventory_results.csv", index=False)


# Apply our algo
service_level = 0.95
z_score = norm.ppf(service_level)

algo_result_df = get_quarterly_restock(demand_df, stock_df, z_score)

print(algo_result_df.head())

# Save results if needed
# algo_result_df.to_csv("../raw_data/low_demand_algo_result.csv", index=False)


# Make comparison
comparison = compare_inventory_models(algo_result_df, naive_results_df, stock_df)

print(comparison)

# Save results
comparison.to_csv("data/low_demand_comparison_summary.csv", index=False)
