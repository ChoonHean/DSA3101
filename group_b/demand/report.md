# Subgroup B – Q1: How can we predict demand for customized products accurately?

## Objective

To predict the demand for customizable products accurately, we developed a demand forecasting pipeline that leverages historical transaction and review data, product metadata, and clustering based on customization patterns. Our goal was to generate robust, cluster-specific quarterly demand forecasts.

----

## Data Cleaning & Preparation

### 1. Metadata (`clean_metadata.py`)
- Cleaned product titles: lowercased, punctuation removed, and lemmatized.
- Removed non-English and duplicate entries.
- Generated sentence embeddings using `SentenceTransformer (MiniLM-L3-v2)`.
- Clustered similar products (customization styles) using MiniBatchKMeans.
- Final number of clusters: **150**

### 2. Reviews (`clean_review.py`)
- Filtered for **verified purchases** only.
- Combined review title + body and removed URLs.
- Extracted sentiment scores using **VADER**, scaled to a 1–5 range.
- Extracted year and quarter from timestamps.

### 3. Combined Dataset (`random_forest_final_df.py`)
- Merged metadata and reviews via `parent_asin`.
- Aggregated at `(cluster_label, year, quarter)` level.
- Final dataset included:
  - `num_sales` (count of verified reviews)
  - `average rating`
  - `average sentiment score`
- Missing time periods filled with 0 sales.
- Output: `combined_dataset.csv`

---

## Model Development

### Feature Engineering
- Added lag features: 1Q to 4Q of previous sales.
- Created a continuous `time_index` feature.
- One-hot encoded cluster labels.
- Applied `log1p()` transformation to stabilize sales values.

### Model: Random Forest Regressor
- Trained to predict `log(num_sales)` per `(cluster_label, quarter)`
- Used `WAPE (Weighted Absolute Percentage Error)` as metric for evaluation
<img width="1206" alt="Screenshot 2025-04-02 at 18 58 44" src="https://github.com/user-attachments/assets/e89e399f-5342-4d87-b706-b2e914478853" />

- Hyperparameter tuning done via `GridSearchCV`
- Best parameters:
  ```python
  {'n_estimators': 500, 'max_depth': None, 'min_samples_split': 2, 'min_samples_leaf': 1}

----

## Predicting Future Demand (`next_year_prediction.py`)

### Workflow:
- Loads `final_combined_dataset.csv` and preprocesses it
- Uses lag features and time index to generate future rows
- Predicts future demand (log scale → original scale)
- Saves results to `dataset/next_year_demand.csv`

### Output Format:
```
cluster_label, year, quarter, predicted_demand
```

---
