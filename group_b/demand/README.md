# Subgroup B – Question 1: How can we predict demand for customized products accurately?

This folder contains the code for demand forecasting of customizable products using historical review and metadata.

---

## How to Run
1. Navigate to **group_b/data_cleaning_scripts** folder
2. Run `clean_metadata.py`, `clean_review.py` to get the clean review and metadata datasets
3. Run `random_forest_final_df.py` to get the final dataset for model training
4. Navigate back to **group_b/demand** folder
5. Run `random_forest_train_df.py` and `random_forest_best_parameter.py` to build a random forest regressor
6. Run `next_year_prediction.py` to get the next year demand prediction
