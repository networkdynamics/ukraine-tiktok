from datetime import datetime
import json
import os
import re

from bertopic import BERTopic
from bertopic.backend._utils import select_backend
import ftlangdetect
import gensim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm

import comment_topics

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', '..', 'data')

    df_path = os.path.join(data_dir_path, 'cache', 'all_english_comments.csv')
    if not os.path.exists(df_path):
        final_comments_df = comment_topics.load_comments_df(limit=None)
        final_comments_df.to_csv(df_path)

    final_comments_df = pd.read_csv(df_path)

    eng_raw_docs = list(final_comments_df['text'].values)
    docs = list(final_comments_df['text_processed'].values)
    timestamps = list(final_comments_df['createtime'].values)

    # Train the model on the corpus.
    pretrained_model = 'cardiffnlp/twitter-roberta-base'

    num_topics = 40
    topic_model = BERTopic(embedding_model=pretrained_model, nr_topics=num_topics)

    #model_path = os.path.join(data_dir_path, 'cache', 'model')

    #if not os.path.exists(model_path):
    # get embeddings so we can cache
    embeddings_cache_path = os.path.join(data_dir_path, 'cache', 'all_english_comment_twitter_roberta_embeddings.npy')
    if os.path.exists(embeddings_cache_path):
        with open(embeddings_cache_path, 'rb') as f:
            embeddings = np.load(f)
    else:
        topic_model.embedding_model = select_backend(pretrained_model,
                                        language=topic_model.language)
        embeddings = topic_model._extract_embeddings(docs,
                                                    method="document",
                                                    verbose=topic_model.verbose)

        with open(embeddings_cache_path, 'wb') as f:
            np.save(f, embeddings)


if __name__ == '__main__':
    main()