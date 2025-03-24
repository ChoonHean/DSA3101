from sklearn.model_selection import GridSearchCV
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from random_forest_train import preprocess, split_train_test

def wape(y_test, y_pred):
    """
    Compute weighted absolute percentage error (WAPE).

    :param y_test: Actual target values in test dataset.
    :param y_pred: Predicted target values in test dataset.
    :return: value of weighted absolute percentage error.
    """
    wape = np.sum(np.abs(y_test - y_pred)) / np.sum(y_test) * 100
    return wape

# Create a scorer object for WAPE
wape_scorer = make_scorer(wape, greater_is_better=False)

if __name__ == '__main__':
    # load dataset
    df = pd.read_csv("../dataset/cleaned_data/final_combined_dataset.csv")

    # preprocess data for splitting
    df = preprocess(df=df)

    # split train-test data
    X_train, X_test, y_train, y_test = split_train_test(df=df, target_col="num_sales", split_year=2021)

    # initialise param_grid for grid search
    param_grid = {
        "n_estimators": [100, 300, 500],
        "max_depth": [10, 20, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4]
    }

    # conduct grid search for hyperparameter tuning of random forest regressor
    rf = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv= 5, scoring=wape_scorer, n_jobs=-1)
    grid_search.fit(X_train, y_train)

    print(f"Best Parameters: {grid_search.best_params_}")
    # Best Parameters: {'max_depth': None, 'min_samples_leaf': 1, 'min_samples_split': 2, 'n_estimators': 500}
