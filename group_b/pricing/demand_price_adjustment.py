import joblib
import pandas as pd


def get_baseprice_pct(parameters):
    """
    Calculate the suggested price adjustment percentage for a product cluster 
    based on forecasted demand and historical baseline demand.

    :param parameters: A dataframe consisting of the parameters required to forecast demand for next quarter
    :param demand_forecast_model: A trained forecasting model that predicts demandbased on cluster, year, and quarter.
    :return: Suggested price adjustment as a decimal (e.g., 0.05 for +5% increase).
    """
    # Load model
    demand_forecast_model = joblib.load("../demand/random_forest_model.joblib")
    # Obtain forecasted demand
    forecasted_demand = demand_forecast_model.predict(parameters)[0]

    # Obtain baseline demand
    baseline_demand = parameters[['num_sales_lag_1Q', 'num_sales_lag_2Q', 'num_sales_lag_3Q',
                                  'num_sales_lag_4Q']].sum().sum() / 4

    # Calculate percentage difference from baseine demand
    demand_diff = (forecasted_demand - baseline_demand) / baseline_demand

    # Suggested price change percentage (assuming PED = - 1.5), should be within -25% to +25%
    price_change = demand_diff / 1.5
    price_change = round(max(min(price_change, 0.25), -0.25) / 0.005) * 0.005

    return price_change


def get_parameters(cluster, year, quarter):
    """
    Returns parameters for the demand forecasting model based on product cluster and current year/quarter.

    :param cluster: The cluster label of the product.
    :param year: The current year for which the price adjustment is calculated.
    :param quarter: The current quarter for which the price adjustment is calculated (1 to 4).
    :return: Suggested price adjustment as a decimal (e.g., 0.05 for +5% increase).
    """
    # Load data set
    df = pd.read_csv("../data/random_forest_dataset.csv")

    # Get time_index of previous quarter
    time_index = year + (quarter - 1) / 4

    # Get parameters for prediction, based on parameters from previous quarter
    df = df[df[f'cluster_{cluster}']]
    parameters = df[df['time_index'] == time_index].copy()
    parameters['num_sales_lag_4Q'] = parameters['num_sales_lag_3Q']
    parameters['num_sales_lag_3Q'] = parameters['num_sales_lag_2Q']
    parameters['num_sales_lag_2Q'] = parameters['num_sales_lag_1Q']
    parameters['num_sales_lag_1Q'] = parameters['num_sales']
    parameters = parameters.drop(columns=['num_sales'])

    return parameters


if __name__ == '__main__':
    # Inputs
    cluster = 2
    year = 2015
    quarter = 2

    # Get parameters for demand prediction
    parameters = get_parameters(cluster, year, quarter)

    # Get recommended percentage of price adjustment
    price_adjustment = f'{get_baseprice_pct(parameters) * 100}%'
    print(price_adjustment)
