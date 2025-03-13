import pandas as pd

df_final_metadata = pd.read_csv("../dataset/cleaned_data/final_cleaned_metadata.csv")
df_final_review = pd.read_csv("../dataset/cleaned_data/final_cleaned_review.csv")

# count num of sales and get avg sentiment score and rating for each quarter
df_review_agg = df_final_review.groupby(['parent_asin', 'year', 'quarter']).agg({
    'review': 'count',
    'sentiment_score': 'mean',
    'rating': 'mean'
}).reset_index()

# rename review count to sales
df_review_agg.rename(columns={'review': 'sales'}, inplace=True)

# join the two dataset
df_combined = df_final_metadata.merge(df_review_agg, on=['parent_asin'], how="left")

# convert to csv
df_combined.to_csv("../dataset/cleaned_data/final_combined_dataset.csv", index=False)
