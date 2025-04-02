# Subgroup B – Question 2: What inventory management strategies will optimize stock levels and minimize costs?

## Objective

This part of the project proposes and implements an inventory management strategy that uses forecasted demand to optimize stock levels and minimize operational costs. The strategy is designed to support customized product inventory at the cluster level while accounting for demand variability and uncertainty in lead time.

---

## Strategy Overview

The inventory strategy combines demand forecasting with classical inventory control concepts:

1. **Forecasted Demand**  
   Demand predictions (`predicted_demand`) are provided by Subgroup B Q1, covering five quarters (Q4 2023 to Q4 2024) for each cluster.

2. **Safety Stock**  
   Safety stock acts a buffer against uncertainties in demand and supply. It is calculated using the standard deviation of moving average demand and lead time (randomized between 0.1 to 3 months) with a service level of 95%. Lead time refers to the total time taken to receive the good after placing a purchase order.  

3. **Reorder Point (ROP)**  
   A reorder point is the critical stock level that signals the need to reorder. It is computed based on average demand and lead time, with safety stock as a buffer.  

   **Formula:**
   ROP = (Average Demand × Lead Time in Quarters) + Safety Stock


4. **Economic Order Quantity (EOQ)**
   EOQ determines the optimal restocking quantity per quarter to minimize ordering and holding costs.  

   **Formula:**
   EOQ = √((2 × D × S) / H)

   Where:
   - D = average demand per quarter
   - S = order cost
   - H = holding cost

---
## Implementation

The script `qn2_inventory_optimization.py` loads the forecasted demand and simulates an optimized inventory strategy using:
- Safety stock (based on demand variability and lead time)
- Reorder point (ROP)
- Economic Order Quantity (EOQ)

The strategy is applied per cluster and quarter, using forecasted demand values. With this strategy, businesses are able to determine when and how much stocks to reorder.    

The code includes detailed inline comments and docstrings explaining each step of the implementation.

---

## Output

The final restocking recommendations are saved in `dataset/quarterly_restock_list.csv`

This output includes the following columns:
- `cluster_label`
- `year_quarter`
- `to_restock` (1 = Yes, 0 = No)
- `optimal_qty` (recommended reorder quantity)

## Scenario Testing: Comparing Inventory Strategies

## Objective

To evaluate the performance of our inventory management algorithm under different business environments, we designed a set of simulation-based scenario tests.

Each scenario compares:
- Our algorithm
- A baseline (naive) strategy with simple reorder rules

---

## Strategies Compared

### 1. **Our Algorithm**
- Reorder if stock ≤ reorder point (based on forecast, EOQ, and lead time)
- Order quantity determined by Economic Order Quantity (EOQ)
- Tracks stock levels, unmet demand (stockouts), and costs

### 2. **Naive Strategy**
The `apply_naive_inventory_strategy()` function used to build naive strategy is defined in `potential_scenarios/normal_scenario.py`.
- Reorder if stock falls below 80% of last quarter’s demand
- Orders 110% of last quarter’s demand
- Uses a fixed safety stock (20% of previous demand)
- Simple rolling stock logic

---

## Performance Metrics
The `compare_inventory_models()` function used to evaluate performance metrics is defined in `potential_scenarios/normal_scenario.py`.

| Metric               | Description |
|----------------------|-------------|
| **Total Unmet Demand** | Total stockouts due to insufficient inventory |
| **Stockout Rate (%)** | Percentage of quarters with stockouts |
| **Service Level (%)** | Percentage of time demand was met |
| **Total Ordering Cost** | Sum of all order quantity × order cost |
| **Avg Holding Cost** | Average holding cost per cluster-quarter |

---

## Scenario 1: Normal Demand (Base Case)
To simulate and compare the naive strategy vs our optimized inventory algorithm under **normal demand**, open the file
`potential_scenarios/simulate_scenarios.py` to generate simulated dataset, then open `potential_scenarios/normal_scenario.py` to test the performance
- Simulated 10 clusters over 4 quarters (2025Q1–2025Q4)
- Base demand: 300–400 units per quarter
- Lead time: 1.0–3.0 months
- Order and holding costs randomized

**Results saved to:**
- `naive_inventory_results.csv`
- `algo_result.csv`
- `comparison_summary.csv`

---

## Other Scenarios

### Scenario 2: High Demand
open the file: `potential_scenarios/high_demand_scenario.py`
- Simulates peak seasons or increased product popularity

### Scenario 3: Low Demand
open the file: `potential_scenarios/low_demand_scenario.py`
- Tests performance in resource-constrained environments

### Scenario 4: Random Demand
open the file: `potential_scenarios/random_demand_scenario.py`
- Tests adaptability to unpredictable market patterns

Each script uses the same logic but adjusts demand and stock to simulate specific environments.

Comparison results will be saved with filenames like:
- `high_demand_comparison_summary.csv`
- `low_demand_comparison_summary.csv`
- `random_demand_comparison_summary.csv`

