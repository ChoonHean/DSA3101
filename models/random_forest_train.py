import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

df = pd.read_csv("../dataset/cleaned_data/final_combined_dataset.csv")

df = df.sort_values(by=["cluster_label", "year", "quarter"])
df["time_index"] = df["year"] + (df["quarter"] - 1) / 4
df["num_sales_lag_1Q"] = df.groupby("cluster_label")["num_sales"].shift(1)
df["num_sales_lag_2Q"] = df.groupby("cluster_label")["num_sales"].shift(2)
df["num_sales_lag_4Q"] = df.groupby("cluster_label")["num_sales"].shift(4)

df = pd.get_dummies(df, columns=["cluster_label"], drop_first=True)

df["num_sales"] = np.log1p(df["num_sales"])

df.fillna(0, inplace=True)

X = df.drop(columns=["num_sales"])
y = df["num_sales"]

split_year = 2021
X_train = X[df["year"] < split_year]
X_test = X[df["year"] >= split_year]
y_train = y[df["year"] < split_year]
y_test = y[df["year"] >= split_year]

best_params = {
    "n_estimators": 500,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42
}

rf_best = RandomForestRegressor(**best_params)
rf_best.fit(X_train, y_train)

y_pred_log = rf_best.predict(X_test)
y_pred_actual = np.expm1(y_pred_log)

y_test_actual = np.expm1(y_test)

joblib.dump(rf_best, "../models/random_forest_model.joblib")

wape = np.sum(np.abs(y_test_actual - y_pred_actual)) / np.sum(y_test_actual) * 100
print(f"Weighted Absolute Percentage Error (WAPE): {wape:.2f}%")
