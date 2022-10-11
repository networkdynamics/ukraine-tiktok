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



def process_comment(comment):
    comment_user = comment['user']
    if isinstance(comment_user, str):
        author_id = comment_user
        author_name = comment_user
    elif isinstance(comment_user, dict):
        if 'unique_id' in comment_user:
            author_id = comment_user['uid']
            author_name = comment_user['unique_id']
        elif 'uniqueId' in comment_user:
            author_id = comment_user['id']
            author_name = comment_user['uniqueId']
        else:
            author_name = ''
            author_id = comment_user['uid']
    else:
        raise Exception()

    comment_text = comment['text']
    return (
        comment['cid'],
        datetime.fromtimestamp(comment['create_time']), 
        author_name,
        author_id, 
        comment_text,
        comment['aweme_id']
    )

def load_comments_df():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    comment_dir_path = os.path.join(data_dir_path, 'comments')

    comments_data = []
    for file_name in tqdm.tqdm(os.listdir(comment_dir_path)):
        file_path = os.path.join(comment_dir_path, file_name, 'video_comments.json')

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r') as f:
            comments = json.load(f)

        comments_data += [process_comment(comment) for comment in comments]
            
    comment_df = pd.DataFrame(comments_data, columns=['comment_id', 'createtime', 'author_name', 'author_id', 'text', 'video_id'])

    comment_df = comment_df[comment_df['text'].notna()]
    comment_df = comment_df[comment_df['text'] != '']
    comment_df = comment_df[comment_df['text'] != 'Nan']

    comment_df['text_no_newlines'] = comment_df['text'].str.replace(r'\n',  ' ', regex=True)
    regex_whitespace = '^[\s ︎]+$' # evil weird whitespace character
    comment_df = comment_df[~comment_df['text_no_newlines'].str.fullmatch(regex_whitespace)]

    # get only english comments
    comment_df['english'] = comment_df['text_no_newlines'].apply(check_english)
    english_comments_df = comment_df[comment_df['english']]

    # tokenize
    english_comments_df['text_processed'] = english_comments_df['text_no_newlines'].apply(preprocess)

    english_comments_df = english_comments_df[english_comments_df['text_processed'].notna()]
    english_comments_df = english_comments_df[english_comments_df['text_processed'] != '']

    # use first 1 mil
    return english_comments_df.iloc[:500000]


def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    df_path = os.path.join(data_dir_path, 'cache', 'half_mil_english_comments.csv')
    if not os.path.exists(df_path):
        final_comments_df = load_comments_df()
        final_comments_df.to_csv(df_path)

    final_comments_df = pd.read_csv(df_path)

    eng_raw_docs = list(final_comments_df['text_no_newlines'].values)
    docs = list(final_comments_df['text_processed'].values)
    timestamps = list(final_comments_df['createtime'].values)

    # Train the model on the corpus.
    pretrained_model = 'cardiffnlp/twitter-roberta-base'

    seed_topic_list = [
        ['zelensky', 'slava', 'ukraine', 'hero'],
        ['china', 'nato', 'biden', 'trump', 'macron', 'boris'],
        ['ura', 'uraa', 'uraaa', 'uraaah', 'putin'],
        ['hilarious', 'love', 'tiktok', 'haha']
    ]

    num_topics = 40
    topic_model = BERTopic(seed_topic_list=None, embedding_model=pretrained_model, nr_topics=num_topics)

    #model_path = os.path.join(data_dir_path, 'cache', 'model')

    #if not os.path.exists(model_path):
    # get embeddings so we can cache
    embeddings_cache_path = os.path.join(data_dir_path, 'cache', 'english_comment_twitter_roberta_embeddings.npy')
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

    topics, probs = topic_model.fit_transform(docs, embeddings)

    outputs_dir_path = os.path.join(data_dir_path, 'outputs')

    topic_df = topic_model.get_topic_info()
    topic_df.to_csv(os.path.join(outputs_dir_path, 'topics.csv'))
    
    hierarchical_topics = topic_model.hierarchical_topics(docs)
    tree = topic_model.get_topic_tree(hierarchical_topics)
    with open(os.path.join(outputs_dir_path, f'{num_topics}_cluster_tree.txt'), 'w') as f:
        f.write(tree)

    topics_over_time = topic_model.topics_over_time(docs, timestamps, nr_bins=150)
    topics_over_time.to_csv(os.path.join(outputs_dir_path, 'topics_over_time.csv'))

    freq_df = topic_model.get_topic_freq()
    freq_df.to_csv(os.path.join(outputs_dir_path, 'topic_freqs.csv'))

    with open(os.path.join(outputs_dir_path, 'topic_labels.json'), 'w') as f:
        json.dump(topic_model.topic_labels_, f)


if __name__ == '__main__':
    main()