import joblib
import pandas as pd
from datetime import date

def get_dynamic_baseprice(cluster, year, quarter, demand_forecast_model):
    """
    Calculate the suggested price adjustment percentage for a product cluster 
    based on forecasted demand and historical baseline demand.

    :param cluster: The cluster label of the product.
    :param year: The current year for which the price adjustment is calculated.
    :param quarter: The current quarter for which the price adjustment is calculated (1 to 4).
    :param demand_forecast_model: A trained forecasting model that predicts demand based on cluster, year, and quarter.
    :return: Suggested price adjustment as a decimal (e.g., 0.05 for +5% increase).
    """
    # Obtain forecasted demand
    input_data = pd.DataFrame({
        'cluster_label': [cluster],
        'year': [year],
        'quarter': [quarter]
    })
    forecasted_demand = demand_forecast_model.predict(input_data)

    # Obtain baseline demand (based on past year)
    previous_periods = []
    for _ in range(4):
        q = quarter - 1
        y = year
        if q < 1:
            q += 4
            y -= 1
        previous_periods.append([y, q])
    baseline_data = pd.DataFrame({
        'cluster_label': [cluster] * len(previous_periods),
        'year': [period[0] for period in previous_periods],
        'quarter': [period[1] for period in previous_periods]
    })
    baseline_demand = demand_forecast_model.predict(baseline_data).mean()

    # Calculate percentage difference from baseine demand
    demand_diff = (forecasted_demand - baseline_demand) / baseline_demand

    # Suggested price change percentage (assuming PED = - 1.5)
    price_change = demand_diff / 1.5
    price_change = round(max(min(price_change, 0.25), -0.25) / 0.005) * 0.005

    return price_change


if __name__ == '__main__':
    # Load model
    demand_forecast_model = joblib.load("../models/random_forest_model.joblib")

    # Get current year/quarter
    year = date.today().year
    month = date.today().month
    quarter = (month - 1) // 3 + 1

    # Input cluster of item (Example)
    cluster = 100

    # Get recommended percentage of price adjustment
    get_dynamic_baseprice(cluster, year, quarter, demand_forecast_model)
