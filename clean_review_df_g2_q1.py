# load dataset
import pandas as pd
df_review = pd.read_json("Amazon_Fashion.jsonl", lines=True)

# select columns
useful_columns = ['title', 'text', 'parent_asin', 'timestamp', 'helpful_vote', 'verified_purchase']
df_review = df_review[useful_columns]

# drop rows where verified_purchase is False
df_review = df_review[df_review['verified_purchase'] == True]

# drop NAs and duplications
df_review.dropna(subset=['parent_asin'], inplace=True)
df_review = df_review.drop_duplicates(subset=['title', 'text', 'parent_asin'])
