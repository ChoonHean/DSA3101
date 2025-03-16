import logging
import os
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.cluster import MiniBatchKMeans
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize

logging.basicConfig(level=logging.INFO)
tqdm.pandas()
os.environ["TOKENIZERS_PARALLELISM"] = "false" # disable tokenizers parallelism for minibatchkmeans
np.random.seed(42)

def clean(text: str) -> str:
    """
    Text cleaning for product title e.g. lowercase, remove non-alphanumeric characters, remove extra spaces

    :param text: Product title
    :return: Cleaned product title
    """
    # lowercase
    text = text.lower()
    # remove non-alphanumeric
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def lemmatize_sentence(lemmatizer, title: str) -> str:
    """
    Convert words in product title to their base forms e.g. running -> run

    :param lemmatizer: A lemmatizer object
    :param title: Product title
    :return: Lemmatized product title
    """
    lemmatized_words = [lemmatizer.lemmatize(word) for word in word_tokenize(title)]
    return " ".join(lemmatized_words)

def get_top_words_per_cluster(tfidf_matrix, num_clusters, clusters, feature_names, top_n=10):
    """
    Extracts the top N words with the highest average TF-IDF scores for each cluster.

    :param tfidf_matrix: A sparse matrix containing the TF-IDF scores.
    :param num_clusters: Total number of clusters.
    :param clusters: A Numpy array containing the cluster label for each product.
    :param feature_names: A list of words (feature names) extracted from the TF-IDF vectorizer.
    :param top_n: The number of top words to retrieve per cluster. Default is 10.
    :return: A dictionary where the keys are cluster labels and the values are lists of the top N words representing each cluster.
    """
    cluster_keywords = {}
    for cluster in tqdm(range(num_clusters), desc="Processing Clusters"):
        # get indices of items in this cluster
        cluster_indices = np.where(clusters == cluster)[0]
        # compute avg TF-IDF per word
        cluster_tfidf = np.mean(tfidf_matrix[cluster_indices].toarray(), axis=0)
        # get top N words
        top_n_idx = cluster_tfidf.argsort()[-top_n:][::-1]
        cols = []
        for i in top_n_idx:
            cols.append(feature_names[i])
        cluster_keywords[cluster] = cols
    return cluster_keywords

def save_cluster_content(num_clusters, clusters, features, top_n=10):
    """
    Processes the top N most representative words for each cluster using TF-IDF. Result is saved as CSV file.
    This function helps in understanding the defining characteristics of each cluster by identifying the top N most frequent words.

    :param num_clusters: Total number of clusters.
    :param clusters: A Numpy array containing the cluster label for each product.
    :param features: Lemmatized product title (that captures the customization features of the product).
    :param top_n: The number of top words to retrieve per cluster. Default is 10.
    :return: None
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(features)
    feature_names = vectorizer.get_feature_names_out()
    top_words_per_cluster = get_top_words_per_cluster(tfidf_matrix, num_clusters, clusters, feature_names, top_n=10)
    df_clusters = pd.DataFrame.from_dict(top_words_per_cluster, orient="index")
    df_clusters.to_csv(f"../dataset/others/top_words_for_{num_clusters}.csv")


if __name__ == "__main__":
    # load dataset
    logging.info("Loading dataset")
    df_meta = pd.read_json("../dataset/raw_data/meta_Amazon_Fashion.jsonl", lines=True)

    # select columns needed
    useful_columns = ['title', 'average_rating', 'parent_asin']
    df_meta = df_meta[useful_columns]

    # remove NAs and duplications
    logging.info("Cleaning dataset")
    df_meta.dropna(subset=['title'], inplace=True)
    df_meta.dropna(subset=['parent_asin'], inplace=True)
    df_meta = df_meta.drop_duplicates(subset=['parent_asin'])
    df_meta = df_meta.reset_index(drop=True)

    logging.info("Dropping rows with non-english titles")
    # remove rows with non-english title for simplicity
    df_meta = df_meta[df_meta['title'].progress_apply(lambda x: x.isascii())].reset_index(drop=True)
    logging.info("Basic text cleaning for titles")
    # text cleaning
    df_meta['title_cleaned'] = df_meta['title'].progress_apply(clean)

    # lemmatize title (for each cluster's visualisation purpose only)
    logging.info("Lemmatize title for visualisation")
    lemmatizer = WordNetLemmatizer()
    df_meta['title_lemma'] = df_meta['title_cleaned'].progress_apply(lambda x: lemmatize_sentence(lemmatizer, x))

    # generate embeddings
    logging.info("Generating embeddings")
    embedding_model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
    embeddings = embedding_model.encode(df_meta['title'], show_progress_bar=True)

    # clustering using MiniBatchKMeans
    logging.info("initialise MiniBatchKMeans")
    num_iterations, batch_size = 20, 10000
    cluster_range = [100, 150, 200]

    # for num_clusters in cluster_range:
    for num_clusters in cluster_range:
        kmeans = MiniBatchKMeans(n_clusters=num_clusters, batch_size=batch_size, random_state=42, n_init=1)

        # train in batches
        with tqdm(total=num_iterations, desc=f"MiniBatchMeans Training for {num_clusters} clusters") as pbar:
            for _ in range(num_iterations):
                batch = embeddings[np.random.choice(embeddings.shape[0], batch_size, replace=False)]
                kmeans.partial_fit(batch)
                pbar.update(1)

        # assign final cluster labels
        cluster_labels = kmeans.predict(embeddings)
        df_meta['cluster_label'] = cluster_labels

        # use lemmatized title to check content of each cluster
        save_cluster_content(num_clusters, cluster_labels, df_meta['title_lemma'], top_n=10)

        logging.info("Save the processed dataset")
        output_path = os.path.abspath(f"../dataset/cleaned_data/cleaned_metadata_{num_clusters}_clusters.csv")
        df_meta.to_csv(output_path, index=False)

    # after checking the best number of clusters, i.e. N=150, clean the final metadata df and save
    best_num_cluster = 150
    final_df = pd.read_csv(f"../dataset/cleaned_data/cleaned_metadata_{best_num_cluster}_clusters.csv")
    final_df.drop(['title_cleaned', 'title_lemma'], axis=1, inplace=True)
    final_df.to_csv(f"../dataset/cleaned_data/final_cleaned_metadata.csv", index=False)



