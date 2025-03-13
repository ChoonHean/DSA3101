import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load dataset and select columns
df_review = pd.read_json("C:\DSA3101\Amazon_Fashion.jsonl", lines=True, nrows = 1000)
useful_columns = ['rating', 'title', 'text', 'parent_asin', 'timestamp', 'verified_purchase']
df_review = df_review[useful_columns]

# Drop rows where verified_purchase is False
df_review = df_review[df_review['verified_purchase']]

# Split timestamp into year and quarter
df_review['year'] = df_review['timestamp'].dt.year
df_review['quarter'] = df_review['timestamp'].dt.quarter

# Combine title and text into a new column
df_review['review'] = df_review['title'] + " " + df_review['text']

# Drop NAs, duplications and unnecessary columns 
df_review.dropna(subset=['parent_asin'], inplace=True)
df_review = df_review.drop_duplicates(subset=['title', 'text', 'parent_asin'])
df_review.drop(columns=['verified_purchase', 'timestamp', 'title', 'text'], inplace=True)


# Sentiment Analysis Score (From 1 - 5) based on Review
# Remove links in review
def remove_url(text):
    url_pattern = r'http\S+|www\S+|https\S+'
    return re.sub(url_pattern, '', text)
df_review['review'] = df_review['review'].apply(remove_url)

# # Use Vader Sentiment pretrained model to calculate a sentiment score from 1 to 5
analyzer = SentimentIntensityAnalyzer()
def get_vader_sentiment(text):
    sentiment = analyzer.polarity_scores(text)
    return round(sentiment['compound'] * 2 + 3, 1)  # Adjust sentiment score range 0 - 5, and round to 1 decimal place

# Apply the function to the 'review' column
df_review['sentiment_score'] = df_review['review'].apply(get_vader_sentiment)

print(df_review.head())

# save the data into csv
df_review.to_csv("../dataset/cleaned_data/final_cleaned_review.csv", index=False)
