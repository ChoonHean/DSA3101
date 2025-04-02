# Subgroup B -  Question 2: What inventory management strategies will optimize stock levels and minimize costs?

## How to Run
To reproduce the inventory optimization logic:  

1. Run `models/qn2_inventory_optimization.py`  
This script loads the forecasted demand from the demand forecasting model `next_year_demand.csv` and simulates an optimized inventory strategy. The output would be a csv file `quarterly_stock_list.csv` that contains the list of products to be restocked.   

To evaluate the performance of our inventory management algorithm under different business environments, we designed a set of simulation-based scenario tests.  

Each scenario compares our algorithm and a baseline (naive) strategy with simple reorder rules.   

1. Run `simulate_scenarios.py`   
This script generates sample datasets for demand and stock, namely `simulated_demand.csv` and `simulated_stock.csv`, which will be used in the scenario tests.  

2. Run `normal_scenario.py` for the first scenario  
This script generates a normal demand scenario, which outputs `comparsion_summary.csv` 

3. Run `high_demand_scenario.py` for the second scenario  
This script generates a high demand scenario, which outputs `high_demand_comparsion_summary.csv`

4. Run `low_demand_scenario.py` for the third scenario  
This script generates a low demand scenario, which outputs `low_demand_comparsion_summary.csv` 

5. Run `random_demand_scenario.py` for the fourth scenario  
This script generates a random demand scenario, which outputs `random_demand_comparison_summary.csv`
