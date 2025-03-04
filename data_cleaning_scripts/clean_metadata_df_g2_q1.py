#load the dataset
import pandas as pd
df_meta = pd.read_json("meta_Amazon_Fashion.jsonl", lines=True)

#select columns needed
useful_columns = ['title', 'average_rating', 'parent_asin']
df_meta = df_meta[useful_columns]

#remove NAs and duplications
df_meta.dropna(subset=['title'], inplace=True)
df_meta.dropna(subset=['parent_asin'], inplace=True)
df_meta = df_meta.drop_duplicates(subset=['parent_asin'])

