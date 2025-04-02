import os

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib


def preprocess(df):
    """
    Preprocesses the raw_data for sales forecasting.

    :param df: Dataframe.
    :return: Preprocessed Dataframe.
    """
    # sort by year and quarter
    df = df.sort_values(by=["cluster_label", "year", "quarter"])

    # create a continuous time index and lagged sales features
    df["time_index"] = df["year"] + (df["quarter"] - 1) / 4
    df["num_sales_lag_1Q"] = df.groupby("cluster_label")["num_sales"].shift(1)
    df["num_sales_lag_2Q"] = df.groupby("cluster_label")["num_sales"].shift(2)
    df["num_sales_lag_3Q"] = df.groupby("cluster_label")["num_sales"].shift(3)
    df["num_sales_lag_4Q"] = df.groupby("cluster_label")["num_sales"].shift(4)

    # remove years before 2013 due to lack of data
    df = df[df["time_index"] >= 2012]

    # one-hot encoding for cluster label
    df['cluster_label'] = df['cluster_label'].astype(int)
    df = pd.get_dummies(df, columns=['cluster_label'], prefix='cluster')
    ohe_cols = sorted([col for col in df.columns if col.startswith('cluster_')],
                      key=lambda x: int(x.split('_')[-1]))
    df = df[[col for col in df.columns if col not in ohe_cols] + ohe_cols]

    # apply log transformation to num_sales and lagged num_sales
    df["num_sales"] = np.log1p(df["num_sales"])
    df["num_sales_lag_1Q"] = np.log1p(df["num_sales_lag_1Q"])
    df["num_sales_lag_2Q"] = np.log1p(df["num_sales_lag_2Q"])
    df["num_sales_lag_3Q"] = np.log1p(df["num_sales_lag_3Q"])
    df["num_sales_lag_4Q"] = np.log1p(df["num_sales_lag_4Q"])

    # remove year and quarter
    df = df.drop(columns=['year', 'quarter'])

    # fill missing values with 0 sales
    df.fillna(0, inplace=True)

    os.makedirs("../data", exist_ok=True)
    df.to_csv("../data/random_forest_dataset.csv", index=False)
    return df


def split_train_test(df, target_col, split_year):
    """
    Splits the raw_data into training and testing sets based on a given year.

    :param df: Preprocessed dataframe.
    :param target_col: The name of target variable.
    :param split_year: The year used to split the train-test data.
    :return: tuple of X_train, X_test, y_train, y_test.
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    X_train = X[df["time_index"] < split_year]
    X_test = X[df["time_index"] >= split_year]
    y_train = y[df["time_index"] < split_year]
    y_test = y[df["time_index"] >= split_year]

    return X_train, X_test, y_train, y_test


def wape(y_test, y_pred):
    """
    Compute weighted absolute percentage error (WAPE).

    :param y_test: Actual target values in test raw_data.
    :param y_pred: Predicted target values in test raw_data.
    :return: value of weighted absolute percentage error.
    """
    wape = np.sum(np.abs(y_test - y_pred)) / np.sum(y_test) * 100
    return wape


if __name__ == '__main__':
    # load final training raw_data
    df = pd.read_csv("../data/combined_dataset.csv")

    # preprocess data for splitting
    df = preprocess(df=df)

    # split train-test data
    X_train, X_test, y_train, y_test = split_train_test(df=df, target_col="num_sales", split_year=2021)

    # got the best params from hyperparameter tuning (grid search)
    best_params = {
        "n_estimators": 500,
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "random_state": 42
    }

    # train random forest regressor
    rf_best = RandomForestRegressor(**best_params)
    rf_best.fit(X_train, y_train)

    # prediction
    y_pred_log = rf_best.predict(X_test)
    y_pred_actual = np.expm1(y_pred_log)

    y_test_actual = np.expm1(y_test)

    # save the trained model for future use
    joblib.dump(rf_best, "random_forest_model.joblib")

    # evaluate model performance using weighted absolute percentage error (WAPE)
    wape = wape(y_test_actual, y_pred_actual)
    print(f"Weighted Absolute Percentage Error (WAPE): {wape:.2f}%")
