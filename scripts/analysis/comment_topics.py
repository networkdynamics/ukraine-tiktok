from datetime import datetime
import json
import os
import re

from bertopic import BERTopic
from bertopic.backend._utils import select_backend
from sklearn.feature_extraction.text import CountVectorizer
import ftlangdetect
import gensim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm

from pytok import utils

MEANINGS = {
    'володимирзеленський': "Ukrainian for 'Volodymr Zelensky'",
    'славаукраїні': "Ukrainian for: 'Glory to Ukraine'",
    'путінхуйло': "Ukrainian for 'Putin sucks'",
    'рек': "Ukrainian for 'Recommended'",
    'україна': "Ukrainian for 'Ukraine'",
    'рекомендации': "Ukrainian for 'Recommendations'",
    'рекомендації': "Ukrainian for 'Recommendations'",
    'россия': "Ukrainian for 'Russia'",
    'украина': "Ukrainian for 'Ukraine'",
    'Україна': "ukrainian for 'Ukraine'",
    'війнавукраїні': "Ukrainian for 'War in Ukraine'",
    'зеленський': "Ukrainian for 'Zelensky'",
    'хочуврек': "Ukrainian for 'I want recommends'?",
    'нівійні': "Ukrainian for 'Non-existent'?",
    'війна': "Ukrainian for 'War'",
    'війна2022': "Ukrainian for 'War2022'",
    'українськийтікток': "Ukrainian for 'Ukrainian TikTok'",
    'президент': "Ukrainian for 'President'",
    'війнатриває': "Ukrainian for 'The War Continues'",
    'українапереможе': "Ukrainian for 'Ukraine will win'",
    'київ': "Ukrainian for 'Kyiv'",
    'макрон': "Ukrainian for 'Macron'",
    'порошенко': "Ukrainian for 'Poroshenko', ex-Prime Minister of Ukraine",
    'европа': "Ukrainian for 'Europe'",
    'nie': "Ukrainian for 'No'",

    'нетвойне': "Russian for 'No war'",
    'тренды': "Russian for 'Trends'",
    'зеленский': "Russian for 'Zelensky'",
    'путинхуйло': "Russian for 'Putin Sucks'",
    'героямслава': "Russian for 'Glory to the Heroes'",
    'юмор': "Russian for 'Funny'",
    'политика': "Russian for 'Politics'",
    'мир': "Russian for 'World' or 'Peace'",
    'переписка': "Russian for 'Correspondence'",
    'Россия': "Russian for 'Russia'",
    'россии': "Russian for 'Russia'",
    'зе': "Russian for 'Ze', Short name for Zelensky?",
    'сша': "Russian for 'USA'",
    'владимирзеленский': "Russian for 'Vladimir Zelensky'",
    'НАТО': "Russian for 'NATO'",
    'донбасс': "Russian for 'Donbass'",
    'просто': "Russian for 'simply'",
    'это': "Russian for 'this'",
    'лучший': "Russian for 'best'",

    'rusia': "Spanish for 'Russia'",
    'parati': "Spanish for 'For You'",
    'ucrania': "Spanish for 'Ukraine'",
    'guerra': "Spanish for 'War'",

    'ucraina': "Romanian for 'Ukraine'",
    
    'путин': "Macedonian for 'Putin'",
    'москва': "Macedonian for 'Moscow'",

    'українапонадусе': "Ukraine above all",
    'ukraina': "Estonian for 'Ukrainian'",
    'perte': "French for 'loss'",
    'fürdich': "German for 'For You'",
    
    'rosja': "Polish for 'Russia'",
    'dlaciebie': "Polish for 'For You'",
    'polska': "Polish for 'Poland'",

    'всебудеукраїна': "All of Ukraine",
    'keşfet': "Turkish for 'Discover'",
    
    'война': "Bulgarian for 'War'",

    'xyzbca': "Common TikTok hashtag that means nothing",
    'зсу': "Armed forces of Ukraine",
    'CapCut': "Video Editor",
}

def preprocess(raw_text):
    text = gensim.utils.to_unicode(raw_text, 'utf8', errors='ignore')
    text = text.lower()
    text = gensim.utils.deaccent(text)
    text = re.sub('@[^ ]+', '@user', text)
    text = re.sub('http[^ ]+', 'http', text)
    return text

def check_english(text):
    try:
        result = ftlangdetect.detect(text)
        return result['lang'] == 'en'
    except Exception as e:
        if str(e) == 'No features in text.':
            return False
        else:
            raise Exception('Unknown error')

def check_for_repeating_tokens(tokens):
    num_tokens = len(tokens)
    num_distinct_tokens = len(set(tokens))
    return (num_tokens / num_distinct_tokens) > 4


def load_comments_df():
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    related_comments_path = os.path.join(data_dir_path, 'cache', 'related_comments.csv')
    comment_df = utils.get_comment_df(related_comments_path)

    comment_df = comment_df[comment_df['text'].notna()]
    comment_df = comment_df[comment_df['text'] != '']
    comment_df = comment_df[comment_df['text'] != 'Nan']
    comment_df = comment_df[comment_df['text'] != 'Null']

    regex_whitespace = '^[\s ︎]+$' # evil weird whitespace character
    comment_df = comment_df[~comment_df['text'].str.fullmatch(regex_whitespace)]

    # get only english comments
    # comment_df['english'] = comment_df['text'].apply(check_english)
    comment_df['english'] = comment_df['comment_language'] == 'en'
    english_comments_df = comment_df[comment_df['english']]

    # tokenize
    english_comments_df['text_processed'] = english_comments_df['text'].apply(preprocess)

    english_comments_df = english_comments_df[english_comments_df['text_processed'].notna()]
    english_comments_df = english_comments_df[english_comments_df['text_processed'] != '']
    english_comments_df = english_comments_df[english_comments_df['text_processed'] != 'Nan']

    return english_comments_df


def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    df_path = os.path.join(data_dir_path, 'cache', 'related_english_comments.csv')
    if not os.path.exists(df_path):
        final_comments_df = load_comments_df()
        final_comments_df.to_csv(df_path)

    final_comments_df = pd.read_csv(df_path)

    eng_raw_docs = list(final_comments_df['text'].values)
    docs = list(final_comments_df['text_processed'].values)
    timestamps = list(final_comments_df['createtime'].values)

    # Train the model on the corpus.
    pretrained_model = 'vinai/bertweet-base'

    num_topics = 40
    vectorizer_model = CountVectorizer(stop_words="english")
    topic_model = BERTopic(embedding_model=pretrained_model, nr_topics=num_topics, vectorizer_model=vectorizer_model)

    # get embeddings so we can cache
    embeddings_cache_path = os.path.join(data_dir_path, 'cache', 'related_english_comment_bertweet_embeddings.npy')
    if os.path.exists(embeddings_cache_path):
        with open(embeddings_cache_path, 'rb') as f:
            embeddings = np.load(f)
    else:
        topic_model.embedding_model = select_backend(pretrained_model,
                                        language=topic_model.language)
        topic_model.embedding_model.embedding_model.max_seq_length = 128
        embeddings = topic_model._extract_embeddings(docs,
                                                    method="document",
                                                    verbose=topic_model.verbose)

        with open(embeddings_cache_path, 'wb') as f:
            np.save(f, embeddings)

    train_size = 500000
    train_docs = docs[:train_size]
    train_embeds = embeddings[:train_size, :]
    train_timestamps = timestamps[:train_size]

    _ = topic_model.fit_transform(train_docs, train_embeds)
    topics, probs = topic_model.transform(docs, embeddings)

    this_run_name = f'related_{num_topics}_bertweet_base'
    run_dir_path = os.path.join(data_dir_path, 'outputs', this_run_name)
    if not os.path.exists(run_dir_path):
        os.mkdir(run_dir_path)

    with open(os.path.join(run_dir_path, 'topics.json'), 'w') as f:
        json.dump([int(topic) for topic in topics], f)

    with open(os.path.join(run_dir_path, 'probs.npy'), 'wb') as f:
        np.save(f, probs)

    topic_df = topic_model.get_topic_info()
    topic_df.to_csv(os.path.join(run_dir_path, 'topic_info.csv'))
    
    hierarchical_topics = topic_model.hierarchical_topics(train_docs)
    hierarchical_topics.to_csv(os.path.join(run_dir_path, 'hierarchical_topics.csv'))

    tree = topic_model.get_topic_tree(hierarchical_topics)
    with open(os.path.join(run_dir_path, f'{num_topics}_cluster_tree.txt'), 'w') as f:
        f.write(tree)

    topics_over_time = topic_model.topics_over_time(train_docs, train_timestamps, nr_bins=150)
    topics_over_time.to_csv(os.path.join(run_dir_path, 'topics_over_time.csv'))

    freq_df = topic_model.get_topic_freq()
    freq_df.to_csv(os.path.join(run_dir_path, 'topic_freqs.csv'))

    with open(os.path.join(run_dir_path, 'topic_labels.json'), 'w') as f:
        json.dump(topic_model.topic_labels_, f)


if __name__ == '__main__':
    main()