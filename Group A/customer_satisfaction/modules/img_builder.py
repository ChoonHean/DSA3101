import matplotlib.pyplot as plt
import nltk
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
from nltk.corpus import stopwords
from wordcloud import WordCloud
from datasets import Dataset
import string


def _clean(text):
    """
    Processes text for natural language processing 
    :param text: String of text.
    :return text: String of processed text.
    """ 
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    text = ' '.join(filtered_words)
    if text == '':
        text = 'none'
    return text

def preprocess(df):
    """
    Takes in a pandas dataframe, and applies one-shot classification to "full_text" column of
    (str) type.
    :param df: Pandas dataframe containing "full_text" column.
    :return df: Pandas dataframe with additional "review_category" column.
    """ 
    df = df.sample(n=10000, random_state=3101)
    df["full_text"] = df["text"].astype(str).apply(_clean)
    if torch.cuda.is_available():
        classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased", device=0)
    else:
        classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
    labels = ["product features", "shipping", "service", "price value", "none"]
    dataset = Dataset.from_pandas(df[['full_text']])
    batch_size = 8
    all_labels = []
  
    for i in range(0, len(dataset), batch_size):
        if i%1000==0:
            print(i)
        batch = dataset[i:i+batch_size]
        texts = batch['full_text']
        results = classifier(texts, candidate_labels=labels)
        all_labels.extend([x['labels'][0] for x in results])
    df['review_category'] = all_labels

    return df

def word_cloud(df, rating, file_dir, tail="right", review_category="all"):
    """
    Creates a word cloud depending on rating and review category.
    :param df: Pandas dataframe containing "rating" and "review_category" column.
    :param rating: Rating integer.
    :param file_dir: Directory to save word cloud image.
    :param tail: Left or right tail of rating.
    :param review_category: Review category for word cloud.
    """
    nltk.download('stopwords')
    reviews = df[df['rating'] >= rating] if tail =="right" else df[df['rating'] <= rating]
    reviews = reviews['review_category'] if (review_category!="all" and "review_category" in reviews.columns) else reviews
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(reviews['full_text'].astype())
    tfidf_scores = X.sum(axis=0).A1
    words = vectorizer.get_feature_names_out()
    word_tfidf = dict(zip(words, tfidf_scores))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_tfidf)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    review_category = "price_value" if review_category=="price value" else review_category
    plt.savefig(f"{file_dir}_{review_category}_{tail}.png")
    plt.close()

def agg_reviews(df, file_dir):
    """
    Save a bar plot of spread of review categories. 
    :param df: Pandas dataframe with "review_category" column.
    :param file_dir: String for file dir to save bar plot.
    """
    reviews_grouped = df.groupby('review_category')["review_id"].nunique().reset_index()
    reviews_grouped = reviews_grouped.rename(columns={"review_id": "review_count"})
    reviews_grouped = reviews_grouped[reviews_grouped["review_category"]!="none"]
    plt.bar(reviews_grouped["review_category"], reviews_grouped["review_count"])
    plt.xlabel('Categories')
    plt.ylabel('Count')
    plt.title('Number of reviews per category')
    plt.savefig(f"{file_dir}reviews_by_categories.png")
    plt.close()

def agg_store(df, file_dir):
    """
    Saves a scatter plot for ratings vs number of reviews for stores.
    :param df: Pandas dataframe containing review and ratings.
    :param file_dir: String for file dir to save scatter plot.
    """
    store_grouped = df.groupby("store").agg(
        num_reviews = ("review_id", "nunique"),
        rating = ("rating", "mean")
    ).reset_index()
    store_grouped = store_grouped[store_grouped["num_reviews"] >= 10]
    plt.scatter(store_grouped["rating"], store_grouped["num_reviews"], s=10)    
    plt.xlabel('Rating')
    plt.ylabel('Number of Reviews')
    plt.savefig(f"{file_dir}rating_reviewcount.png")
    plt.close()