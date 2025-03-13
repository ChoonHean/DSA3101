import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV

# Load dataset
df = pd.read_csv("../dataset/cleaned_data/final_combined_dataset.csv")

# Sort dataset
df = df.sort_values(by=['parent_asin', 'year', 'quarter']).reset_index(drop=True)

# Apply log transformation
df['sales'] = np.log1p(df['sales'])

# create lagged sales features
df['prev_sales_1Q'] = df.groupby('parent_asin')['sales'].shift(1)
df['prev_sales_2Q'] = df.groupby('parent_asin')['sales'].shift(2)
df['prev_sales_4Q'] = df.groupby('parent_asin')['sales'].shift(4)

# drop NA due to lag features
df = df.dropna()

# Define features and target
features = ['prev_sales_1Q', 'prev_sales_2Q', 'prev_sales_4Q', 'sentiment_score', 'rating']
target = 'sales'

X = df[features]
y = df[target]

# Split dataset into train and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

# Define hyperparameter grid
param_dist = {
    'n_estimators': np.arange(100, 1000, 100),  # Number of trees
    'max_depth': [5, 10, 20, None],  # Depth of trees
    'min_samples_split': np.arange(2, 20, 2),  # Minimum samples to split a node
    'min_samples_leaf': np.arange(1, 10, 2)  # Minimum samples per leaf
}

# Initialize the Random Forest model
rf = RandomForestRegressor(random_state=42, n_jobs=-1)

# Perform Randomized Search
random_search = RandomizedSearchCV(
    rf, param_dist,
    n_iter=20,
    cv=3,
    scoring='neg_mean_squared_error',
    n_jobs=-1,
    random_state=42
)

# Fit the model
random_search.fit(X_train, y_train)

# Get the best parameters
best_params = random_search.best_params_
print("Best Hyperparameters:", best_params)

# Train the final model with the best parameters
best_rf = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
best_rf.fit(X_train, y_train)

# Evaluate the model
y_pred = best_rf.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"Test RMSE: {rmse:.2f}")
print("Mean sales per quarter:", df['sales'].mean())
print("RMSE as % of mean sales:", (rmse / df['sales'].mean()) * 100, "%")


# Best Hyperparameters: {'n_estimators': np.int64(800), 'min_samples_split': np.int64(8), 'min_samples_leaf': np.int64(1), 'max_depth': 20}
# Test RMSE: 0.30
# Mean sales per quarter: 1.0692575629538235
# RMSE as % of mean sales: 27.67813986391849 %

