from datetime import datetime
import json
import os
import random
from typing import final

from octis.dataset.dataset import Dataset
from topicx.baselines.cetopictm import CETopicTM
from topicx.baselines.lda import LDATM
import ftlangdetect
import gensim
from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import numpy as np
import pandas as pd
import tqdm


def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', '..', 'data')

    df_path = os.path.join(data_dir_path, 'cache', 'half_mil_english_comments.csv')
    if os.path.exists(df_path):
        final_comments_df = pd.read_csv(df_path)
        final_comments_df['no_stopwords_tokens'] = final_comments_df['no_stopwords_tokens'].apply(str_to_list)
    else:
        final_comments_df = load_comments_df()

    embeddings_cache_path = os.path.join(data_dir_path, 'cache', 'english_comment_twitter_roberta_embeddings.npy')
    if os.path.exists(embeddings_cache_path):
        with open(embeddings_cache_path, 'rb') as f:
            embeddings = np.load(f)
    else:
        embeddings = None

    final_comments_df = final_comments_df.iloc[:500000]
    embeddings = embeddings[:500000]

    eng_raw_docs = list(final_comments_df['text_no_newlines'].values)
    docs = list(final_comments_df['no_stopwords_tokens'].values)

    dataset = Dataset(docs)

    # Train the model on the corpus.
    #for num_topics in [4, 6, 8, 10, 12, 14, 16]:
    num_topics = 6
    topic_model = 'cetopic'
    seed = 42
    dim_size = -1
    word_select_method = 'tfidf_idfi'
    pretrained_model = 'cardiffnlp/twitter-roberta-base'

    if topic_model == 'cetopic':
        tm = CETopicTM(dataset=dataset, 
                       topic_model=topic_model, 
                       num_topics=num_topics, 
                       dim_size=dim_size, 
                       word_select_method=word_select_method,
                       embedding=pretrained_model, 
                       seed=seed)
    elif topic_model == 'lda':
        tm = LDATM(dataset, topic_model, num_topics)

    tm.train(embeddings=embeddings)

    td_score, cv_score, npmi_score = tm.evaluate()
    print(f'Model {topic_model} num_topics: {num_topics} td: {td_score} npmi: {npmi_score} cv: {cv_score}')
    
    topics = tm.get_topics()

    sample_method = 'random'

    distances = tm.distances
    for topic_num in topics:
        print(f"Topic number: {topic_num}")
        print(topics[topic_num])
        num_sample = 10
        if sample_method == 'random':
            comment_idx = random.sample([idx for (idx, topic) in enumerate(tm.topics) if topic == topic_num], num_sample)
        elif sample_method == 'closest':
            comment_idx = np.argsort(distances[:, topic_num])[:num_sample]
        for idx in comment_idx:
            print(eng_raw_docs[idx])

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    topic_markers = ['o', '*', '^', 's', '+', 'D']
    for topic_num in topics:
        topic_indices = [idx for (idx, topic) in enumerate(tm.topics) if topic == topic_num]
        topic_embeddings = embeddings[topic_indices]
        marker = topic_markers[topic_num]
        ax.scatter(topic_embeddings[:,0], topic_embeddings[:,1], topic_embeddings[:,2], marker=marker)

    fig_path = os.path.join(data_dir_path, '..', 'figs', 'clusters.png')
    plt.savefig(fig_path)


if __name__ == '__main__':
    main()