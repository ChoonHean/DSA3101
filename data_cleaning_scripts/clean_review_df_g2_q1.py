import os
import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def remove_url(text: str) -> str:
    """
    Remove url from review text.

    :param text: Review text
    :return: Cleaned review text
    """
    url_pattern = r'http\S+|www\S+|https\S+'
    return re.sub(url_pattern, '', text)

def get_vader_sentiment(text):
    """
    Computes the sentiment score of a given text using the VADER sentiment analysis model.

    :param text: Review text.
    :return: Sentiment score range from 1 to 5, round to 1 decimal place.
    """
    sentiment = analyzer.polarity_scores(text)
    return round(sentiment['compound'] * 2 + 3, 1)

if __name__ == "__main__":
    # Load dataset and select columns
    df_review = pd.read_json("../dataset/raw_data/Amazon_Fashion.jsonl", lines=True)
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

    # Remove links in review
    df_review['review'] = df_review['review'].apply(remove_url)

    # Use Vader Sentiment pretrained model to calculate a sentiment score from 1 to 5
    analyzer = SentimentIntensityAnalyzer()
    df_review['sentiment_score'] = df_review['review'].apply(get_vader_sentiment)
    print(df_review.head())

    # Save the data into csv
    os.makedirs("../dataset/cleaned_data", exist_ok=True)
    df_review.to_csv("../dataset/cleaned_data/final_cleaned_review.csv", index=False)
