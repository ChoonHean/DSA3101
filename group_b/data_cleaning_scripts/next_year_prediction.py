import numpy as np
import pandas as pd
import joblib

def preprocess(df):
    """
    Preprocesses the input DataFrame for time-series demand forecasting.

    This function prepares the raw_data by:
    - Sorting data chronologically by cluster, year, and quarter
    - Creating a continuous time index
    - Generating lag features for 'num_sales' (1Q to 4Q)
    - Applying one-hot encoding to 'cluster_label'
    - Reordering columns so that one-hot encoded columns are at the end
    - Applying log transformation to 'num_sales'
    - Filling any missing values (especially in lag columns) with 0

    Parameters:
        df (pd.DataFrame): Raw input data containing columns 
                           ['cluster_label', 'year', 'quarter', 'num_sales']

    Returns:
        pd.DataFrame: Preprocessed DataFrame ready for training or prediction.
    """
    df = df.sort_values(by=["cluster_label", "year", "quarter"])
    df["time_index"] = df["year"] + (df["quarter"] - 1) / 4.0

    # Add lag features (1Q to 4Q)
    df["num_sales_lag_1Q"] = df.groupby("cluster_label")["num_sales"].shift(1)
    df["num_sales_lag_2Q"] = df.groupby("cluster_label")["num_sales"].shift(2)
    df["num_sales_lag_3Q"] = df.groupby("cluster_label")["num_sales"].shift(3)
    df["num_sales_lag_4Q"] = df.groupby("cluster_label")["num_sales"].shift(4)

    # One-hot encode cluster_label
    df["cluster_label"] = df["cluster_label"].astype(int)
    df = pd.get_dummies(df, columns=["cluster_label"], prefix="cluster")

    # Sort dummy columns to end
    ohe_cols = sorted([col for col in df.columns if col.startswith("cluster_")],
                      key=lambda x: int(x.split("_")[-1]))
    df = df[[col for col in df.columns if col not in ohe_cols] + ohe_cols]

    # Log-transform sales
    df["num_sales"] = np.log1p(df["num_sales"])

    # Fill missing lag values
    df.fillna(0, inplace=True)

    return df

def create_future_data_single_step(df, future_year, future_quarter):
    """
    Create one row of future input data per cluster for the specified future year and quarter.

    Parameters:
        df (pd.DataFrame): Preprocessed historical data.
        future_year (int): Year of prediction (e.g., 2024).
        future_quarter (int): Quarter of prediction (1 to 4).

    Returns:
        pd.DataFrame: Future input data ready for model prediction.
    """
    cluster_cols = [col for col in df.columns if col.startswith("cluster_")]
    unique_clusters = df[cluster_cols].drop_duplicates()

    future_rows = []
    for _, cluster_row in unique_clusters.iterrows():
        mask = (df[cluster_cols] == cluster_row.values).all(axis=1)
        cluster_df = df[mask].sort_values(by="time_index")

        last_row = cluster_df.iloc[-1].copy()
        new_row = last_row.copy()
        new_row["time_index"] = future_year + (future_quarter - 1) / 4.0

        new_row["num_sales_lag_1Q"] = last_row["num_sales"]
        new_row["num_sales_lag_2Q"] = last_row["num_sales_lag_1Q"]
        new_row["num_sales_lag_3Q"] = last_row["num_sales_lag_2Q"]
        new_row["num_sales_lag_4Q"] = last_row["num_sales_lag_3Q"]

        new_row["num_sales"] = 0
        new_row["year"] = future_year
        new_row["quarter"] = future_quarter

        future_rows.append(new_row)

    future_df = pd.DataFrame(future_rows)
    return future_df

def forecast_multiple_quarters(rf_model, df, start_year, start_quarter, steps):
    """
        Iteratively generate forecasts for the next `steps` quarters.

        Parameters:
            rf_model (RandomForestRegressor): Trained model.
            df (pd.DataFrame): Preprocessed historical data.
            start_year (int): Year to begin forecasting from.
            start_quarter (int): Quarter to begin forecasting from.
            steps (int): Number of quarters to forecast.

        Returns:
            pd.DataFrame: Forecasted data including predicted demand per cluster and quarter.
    """
    df_forecast = df.copy()
    current_year = start_year
    current_quarter = start_quarter
    future_predictions = []

    # Determine feature columns: drop target and time-only fields
    all_cols = df.columns.tolist()
    feature_cols = [col for col in all_cols if col not in ["num_sales", "year", "quarter"]]

    for _ in range(steps):
        future_data = create_future_data_single_step(df_forecast, current_year, current_quarter)

        # Ensure all features present
        for col in feature_cols:
            if col not in future_data.columns:
                future_data[col] = 0

        X_future = future_data[feature_cols].copy()

        y_pred_log = rf_model.predict(X_future)
        y_pred_actual = np.expm1(y_pred_log)

        future_data["predicted_demand"] = y_pred_actual
        future_data["num_sales"] = np.log1p(y_pred_actual)

        df_forecast = pd.concat([df_forecast, future_data.drop(columns=["year", "quarter"])], ignore_index=True)
        future_predictions.append(future_data)

        if current_quarter == 4:
            current_quarter = 1
            current_year += 1
        else:
            current_quarter += 1

    return pd.concat(future_predictions, ignore_index=True)

def revert_cluster_dummies(df, dummy_prefix="cluster_", baseline_category="0"):
    """
        Convert one-hot encoded cluster columns back into a single `cluster_label` column.

        Parameters:
            df (pd.DataFrame): DataFrame with one-hot encoded cluster columns.
            dummy_prefix (str): Prefix used in one-hot encoded columns.
            baseline_category (str): Label for the implicit category (if all zeros).

        Returns:
            pd.DataFrame: DataFrame with a single `cluster_label` column.
    """
    dummy_cols = [col for col in df.columns if col.startswith(dummy_prefix)]

    def get_cluster_label(row):
        if row[dummy_cols].sum() == 0:
            return baseline_category
        else:
            return row[dummy_cols].idxmax().replace(dummy_prefix, "")

    df["cluster_label"] = df.apply(get_cluster_label, axis=1)
    return df

if __name__ == '__main__':
    # Load and preprocess original raw_data
    df = pd.read_csv("../cleaned_data/final_combined_dataset.csv")
    df_preprocessed = preprocess(df)

    # Load trained model
    rf_model = joblib.load("../group_b/models/random_forest_model.joblib")

    # Forecast demand for 5 quarters from Q4 2023
    future_preds = forecast_multiple_quarters(
        rf_model, df_preprocessed, start_year=2023, start_quarter=4, steps=5
    )

    # Revert cluster dummies for readable output
    future_preds = revert_cluster_dummies(future_preds, dummy_prefix="cluster_", baseline_category="0")

    # Format and save final output
    future_preds["predicted_demand"] = future_preds["predicted_demand"].round().astype(int)
    output = future_preds[["cluster_label", "year", "quarter", "predicted_demand"]]
    output = output.sort_values(by=["cluster_label", "year", "quarter"])

    print(output)

    output.to_csv("../raw_data/next_year_demand.csv", index=False)
