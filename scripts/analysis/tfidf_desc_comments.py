from datetime import datetime
import json
import os

import networkx as nx
import pandas as pd
import tqdm
import numpy as np
import scipy.sparse as sp

from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

class CTFIDFVectorizer(TfidfTransformer):
    def __init__(self, *args, **kwargs):
        super(CTFIDFVectorizer, self).__init__(*args, **kwargs)

    def fit(self, X: sp.csr_matrix, n_samples: int):
        """Learn the idf vector (global term weights) """
        _, n_features = X.shape
        df = np.squeeze(np.asarray(X.sum(axis=0)))
        idf = np.log(n_samples / df)
        self._idf_diag = sp.diags(idf, offsets=0,
                                  shape=(n_features, n_features),
                                  format='csr',
                                  dtype=np.float64)
        return self

    def transform(self, X: sp.csr_matrix) -> sp.csr_matrix:
        """Transform a count-based matrix to c-TF-IDF """
        X = X * self._idf_diag
        X = normalize(X, axis=1, norm='l1', copy=False)
        return X

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    comment_dir_path = os.path.join(data_dir_path, 'comments')

    comments = []
    for file_name in tqdm.tqdm(os.listdir(comment_dir_path)):
        file_path = os.path.join(comment_dir_path, file_name, 'video_comments.json')

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r') as f:
            comment_data = json.load(f)

        comments += comment_data

    comments_data = []
    for comment in comments:
        if isinstance(comment['user'], str):
            author = comment['user']
        elif isinstance(comment['user'], dict):
            if 'unique_id' in comment['user']:
                author = comment['user']['unique_id']
            elif 'uniqueId' in comment['user']:
                author = comment['user']['uniqueId']
            else:
                author = comment['user']['uid']
        else:
            raise Exception()

        comments_data.append((
            datetime.fromtimestamp(comment['create_time']), 
            author, 
            comment['text'],
            comment['aweme_id']
        ))

    comment_df = pd.DataFrame(comments_data, columns=['createtime', 'author', 'text', 'video_id'])

    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
               + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

    videos = []
    for file_path in tqdm.tqdm(file_paths):
        with open(file_path, 'r') as f:
            video_data = json.load(f)
        videos += video_data

    vids_data = [
        (
            video['id'],
            datetime.fromtimestamp(video['createTime']), 
            video['author']['uniqueId'], 
            video['desc'], 
            [challenge['title'] for challenge in video.get('challenges', [])]
        ) 
        for video in videos
    ]

    video_df = pd.DataFrame(vids_data, columns=['id', 'createtime', 'author', 'desc', 'hashtags'])
    video_df = video_df.drop_duplicates('id')

    # Create documents per label
    hashtags_df = video_df.explode('hashtags')

    NUM_TOP_HASHTAGS = 20
    top_hashtags_df = hashtags_df.groupby('hashtags')['desc'].count().sort_values(ascending=False).head(NUM_TOP_HASHTAGS)
    top_hashtags = set(top_hashtags_df.index)
    docs_per_class = hashtags_df[hashtags_df['hashtags'].isin(top_hashtags)].groupby('hashtags')[['desc']].agg(' '.join)

    # Create c-TF-IDF
    count_vectorizer = CountVectorizer().fit(docs_per_class['desc'])
    count = count_vectorizer.transform(docs_per_class['desc'])
    words = count_vectorizer.get_feature_names()

    # Extract top 10 words per class
    ctfidf = CTFIDFVectorizer().fit_transform(count, n_samples=len(hashtags_df)).toarray()
    words_per_class = {label: [words[index] for index in ctfidf[idx].argsort()[-10:]] 
                    for idx, label in enumerate(docs_per_class.index.to_list())}

    print(json.dumps(words_per_class, indent=4, ensure_ascii=False))

    video_comments_df = video_df.rename(columns={'createtime': 'video_createtime', 'id': 'video_id', 'author': 'video_author', 'desc': 'video_desc', 'hashtags': 'video_hashtags'}) \
        .merge(comment_df.rename(columns={'createtime': 'comment_createtime', 'author': 'comment_author', 'text': 'comment_text'}), on='video_id')

    hashtag_comments_df = video_comments_df.explode('video_hashtags') \
                                           .groupby(['video_id', 'video_hashtags'])[['comment_text']] \
                                           .agg(' '.join) \
                                           .reset_index()

    comments_per_hashtag_df = hashtag_comments_df[hashtag_comments_df['video_hashtags'].isin(top_hashtags)].groupby('video_hashtags')[['comment_text']].agg(' '.join)

    # Create c-TF-IDF
    count_vectorizer = CountVectorizer().fit(comments_per_hashtag_df['comment_text'])
    count = count_vectorizer.transform(comments_per_hashtag_df['comment_text'])
    words = count_vectorizer.get_feature_names()

    # Extract top 10 words per class
    ctfidf = CTFIDFVectorizer().fit_transform(count, n_samples=len(hashtags_df)).toarray()
    words_per_class = {label: [words[index] for index in ctfidf[idx].argsort()[-10:]] 
                    for idx, label in enumerate(comments_per_hashtag_df.index.to_list())}

    print(json.dumps(words_per_class, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()