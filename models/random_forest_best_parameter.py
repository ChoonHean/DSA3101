from sklearn.model_selection import GridSearchCV
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("../dataset/cleaned_data/final_combined_dataset.csv")

df = df.sort_values(by=["cluster_label", "year", "quarter"])
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

param_grid = {
    "n_estimators": [100, 300, 500],
    "max_depth": [10, 20, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4]
}

rf = RandomForestRegressor(random_state=42)
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv= 5, scoring="neg_root_mean_squared_error", n_jobs=-1)
grid_search.fit(X_train, y_train)

print(f"Best Parameters: {grid_search.best_params_}")

# Best Parameters: {'max_depth': None, 'min_samples_leaf': 1, 'min_samples_split': 2, 'n_estimators': 500}