import numpy as np
import pandas as pd
import joblib

def preprocess(df):
    df = df.sort_values(by=["cluster_label", "year", "quarter"])
    df["time_index"] = df["year"] + (df["quarter"] - 1) / 4.0
    df["num_sales_lag_1Q"] = df.groupby("cluster_label")["num_sales"].shift(1)
    df["num_sales_lag_2Q"] = df.groupby("cluster_label")["num_sales"].shift(2)
    df["num_sales_lag_4Q"] = df.groupby("cluster_label")["num_sales"].shift(4)
    df = pd.get_dummies(df, columns=["cluster_label"], drop_first=True)
    df["num_sales"] = np.log1p(df["num_sales"])
    df.fillna(0, inplace=True)
    return df


def create_future_data_single_step(df, future_year, future_quarter):
    """
    Create a new row for each cluster for the specified future quarter.
    Lag features are filled using the most recent available (or predicted) data.
    """
    cluster_cols = [col for col in df.columns if col.startswith("cluster_label_")]
    unique_clusters = df[cluster_cols].drop_duplicates()

    future_rows = []
    for _, cluster_row in unique_clusters.iterrows():
        mask = (df[cluster_cols] == cluster_row.values).all(axis=1)
        cluster_df = df[mask].sort_values(by=["year", "quarter"])
        # Get the most recent row
        last_row = cluster_df.iloc[-1].copy()
        # Create a new row for the future quarter
        new_row = last_row.copy()
        new_row["year"] = future_year
        new_row["quarter"] = future_quarter
        new_row["time_index"] = future_year + (future_quarter - 1) / 4.0
        # Update lag features:
        new_row["num_sales_lag_1Q"] = last_row["num_sales"]
        new_row["num_sales_lag_2Q"] = last_row["num_sales_lag_1Q"]
        new_row["num_sales_lag_4Q"] = last_row.get("num_sales_lag_4Q", 0)

        new_row["num_sales"] = 0
        future_rows.append(new_row)

    future_df = pd.DataFrame(future_rows)
    return future_df


def forecast_multiple_quarters(rf_model, df, feature_cols, start_year, start_quarter, steps):
    """
    Iteratively forecast for a given number of future quarters.

    :param rf_model: Trained RandomForestRegressor model.
    :param df: Preprocessed DataFrame with historical data.
    :param feature_cols: List of feature columns used during training.
    :param start_year: Starting year for forecasting (e.g., 2023).
    :param start_quarter: Starting quarter (e.g., 4 for Q4 2023).
    :param steps: Total number of quarters to forecast.
    :return: DataFrame containing predictions for the future quarters.
    """
    df_forecast = df.copy()
    current_year = start_year
    current_quarter = start_quarter
    future_predictions = []

    for i in range(steps):
        # Create future data row(s) for the current quarter
        future_data = create_future_data_single_step(df_forecast, current_year, current_quarter)

        # Select only the training features
        X_future = future_data[feature_cols].copy()

        # Predict in log space and then convert predictions back to actual values
        y_pred_log = rf_model.predict(X_future)
        y_pred_actual = np.expm1(y_pred_log)

        future_data["predicted_demand"] = y_pred_actual
        # Update 'num_sales' for iterative forecasting using the log-transformed prediction
        future_data["num_sales"] = np.log1p(y_pred_actual)

        # Append the new rows to the forecast DataFrame for subsequent predictions
        df_forecast = pd.concat([df_forecast, future_data], ignore_index=True)
        future_predictions.append(future_data)

        # Update to next quarter
        if current_quarter == 4:
            current_quarter = 1
            current_year += 1
        else:
            current_quarter += 1

    future_preds_df = pd.concat(future_predictions, ignore_index=True)
    return future_preds_df


def revert_cluster_dummies(df, dummy_prefix="cluster_label_", baseline_category="A"):
    """
    Reverts dummy-encoded cluster columns back to a single categorical column.

    Parameters:
      df: DataFrame containing the dummy columns.
      dummy_prefix: The prefix of the dummy columns.
      baseline_category: The category for rows where all dummy columns are 0.

    Returns:
      df with a new column "cluster_label_original" containing the reverted labels.
    """
    # Identify dummy columns
    dummy_cols = [col for col in df.columns if col.startswith(dummy_prefix)]

    def get_cluster_label(row):
        # If all dummy columns are 0, then this row belongs to the baseline category
        if row[dummy_cols].sum() == 0:
            return baseline_category
        else:
            # Otherwise, find the dummy column that is 1 and remove the prefix
            return row[dummy_cols].idxmax().replace(dummy_prefix, "")

    df["cluster_label"] = df.apply(get_cluster_label, axis=1)
    return df


if __name__ == '__main__':
    # Import the dataset
    df = pd.read_csv("../dataset/cleaned_data/final_combined_dataset.csv")

    # Preprocess the dataset (assumes data up to 2023 Q3)
    df_preprocessed = preprocess(df)

    # Load the saved model
    rf_model = joblib.load("../models/random_forest_model.joblib")

    # Determine the feature columns used during training
    trained_feature_cols = [col for col in df_preprocessed.columns if col != "num_sales"]

    # Forecast for 2023 Q4 and all four quarters of 2024
    future_preds = forecast_multiple_quarters(
        rf_model, df_preprocessed, trained_feature_cols, start_year=2023, start_quarter=4, steps=5
    )

    # Convert the dummies
    future_preds_with_cluster = revert_cluster_dummies(future_preds, dummy_prefix="cluster_label_",
                                                       baseline_category="0")

    # Round predicted_sales and convert to integer
    future_preds_with_cluster["predicted_demand"] = future_preds_with_cluster["predicted_demand"].round().astype(int)

    # Select only the desired columns
    final_output = future_preds_with_cluster[["cluster_label", "year", "quarter", "predicted_demand"]]
    final_output = final_output.sort_values(by=["cluster_label", "year", "quarter"])

    print(final_output)

    # Save the final data into csv
    final_output.to_csv("../dataset/next_year_demand.csv", index=False)
