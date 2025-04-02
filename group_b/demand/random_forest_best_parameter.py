from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from random_forest_train import preprocess, split_train_test, wape

if __name__ == '__main__':
    # load raw_data
    df = pd.read_csv("../cleaned_data/combined_dataset.csv")

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

    # Create a scorer object for WAPE
    wape_scorer = make_scorer(wape, greater_is_better=False)

    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv= 5, scoring=wape_scorer, n_jobs=-1)
    grid_search.fit(X_train, y_train)

    print(f"Best Parameters: {grid_search.best_params_}")
    # Best Parameters: {'max_depth': None, 'min_samples_leaf': 1, 'min_samples_split': 2, 'n_estimators': 500}
