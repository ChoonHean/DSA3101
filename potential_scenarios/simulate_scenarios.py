import pandas as pd
import numpy as np

# Set a random seed for reproducibility
np.random.seed(42)

# Define the number of clusters and quarters
clusters = range(10)
quarters = pd.period_range("2025Q1", "2025Q4", freq="Q")

# Generate a demand dataset with higher values
data = []
for cluster in clusters:
    base_demand = np.random.randint(300, 400)
    for quarter in quarters:
        demand_variation = np.random.randint(-50, 50)
        predicted_demand = max(50, base_demand + demand_variation)
        date = quarter.to_timestamp()
        data.append([cluster, date, predicted_demand])

# Create DataFrame
demand_df = pd.DataFrame(data, columns=["cluster_label", "date", "predicted_demand"])

# Save the dataset
demand_df.to_csv("../dataset/simulated_demand.csv", index=False)

# Generate stock dataset
stock_data = []
for cluster in clusters:
    stock_quantity = np.random.randint(300, 400)
    lead_time_months = np.random.uniform(1, 3)
    order_cost = np.random.randint(30, 80)
    holding_cost = np.random.uniform(1, 10)

    stock_data.append([cluster, stock_quantity, round(lead_time_months, 2), order_cost, round(holding_cost, 2)])

# Create DataFrame
stock_df = pd.DataFrame(stock_data, columns=["cluster_label", "stock_quantity", "lead_time_months", "order_cost", "holding_cost"])

# Save to CSV
stock_df.to_csv("../dataset/simulated_stock.csv", index=False)
