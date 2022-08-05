from datetime import datetime
import json
import os
import re

import gensim
from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS
import ftlangdetect
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
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

class NGrams:
    def __init__(self, docs):
        self.bigram = Phrases(docs, connector_words=ENGLISH_CONNECTOR_WORDS)

    def add_ngrams(self, tokens):
        # Token is a bigram, add to document
        bigrams = [token for token in self.bigram[tokens] if '_' in token]
        tokens.extend(bigrams)
        return tokens

class Lemmatizer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def lemmatize(self, tokens):
        return [self.lemmatizer.lemmatize(token) for token in tokens]

class StopwordRemover:
    def __init__(self):
        this_dir_path = os.path.dirname(os.path.abspath(__file__))
        data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
        languages = ['english', 'russian', 'french', 'spanish', 'german']
        self.all_stopwords = set()
        for language in languages:
            self.all_stopwords.update(stopwords.words(language))
        ukraine_stopwords_path = os.path.join(data_dir_path, 'stopwords', 'stopwords_ua.txt')
        with open(ukraine_stopwords_path, 'r') as f:
            ukraine_stopwords = f.readlines()
        self.all_stopwords.update(ukraine_stopwords)

    def remove_stopwords(self, tokens):
        return [token for token in tokens if token not in self.all_stopwords]

class LDATopTopic:
    def __init__(self, lda):
        self.lda = lda

    def get_top_topic(self, raw_doc, tokens, bow):
        topics = self.lda.get_document_topics(bow)
        top_topic = max(topics, key = lambda topic: topic[1])
        return (raw_doc, tokens, top_topic[0], top_topic[1])

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

def main():
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
    comment_df['text_no_newlines'] = comment_df['text'].str.replace(r'\n',  ' ', regex=True)

    # get only english comments
    comment_df['english'] = comment_df['text_no_newlines'].apply(check_english)
    english_comments_df = comment_df[comment_df['english']]

    # tokenize
    english_comments_df['tokens'] = english_comments_df['text_no_newlines'].apply(gensim.utils.simple_preprocess)

    

    # Add bigrams and trigrams to docs
    ngrams = NGrams(english_comments_df['tokens'].values)
    english_comments_df['ngram_tokens'] = english_comments_df['tokens'].apply(ngrams.add_ngrams)

    # lemmatize
    lemmatizer = Lemmatizer()
    english_comments_df['lemmatized_tokens'] = english_comments_df['ngram_tokens'].apply(lemmatizer.lemmatize)

    # remove stop words
    stopword_remover = StopwordRemover()
    english_comments_df['no_stopwords_tokens'] = english_comments_df['lemmatized_tokens'].apply(stopword_remover.remove_stopwords)

    final_comments_df = english_comments_df[english_comments_df['no_stopwords_tokens'].astype(bool)]

    eng_raw_docs = list(final_comments_df['text_no_newlines'].values)
    docs = list(final_comments_df['no_stopwords_tokens'].values)

    # Create a corpus from a list of texts
    comments_dictionary = gensim.corpora.dictionary.Dictionary(docs)
    comments_dictionary.filter_extremes(no_below=20, no_above=0.5)

    comments_corpus = [comments_dictionary.doc2bow(text) for text in docs]

    # Make an index to word dictionary.
    _ = comments_dictionary[0]  # This is only to "load" the dictionary.
    id2word = comments_dictionary.id2token

    # Train the model on the corpus.
    for num_topics in [4, 6, 8, 10, 12, 14, 16]:
        lda = gensim.models.ldamulticore.LdaMulticore(comments_corpus, num_topics=num_topics, id2word=id2word)

        # determine most topic focused documents
        lda_top_topic = LDATopTopic(lda)
        topic_docs = [lda_top_topic.get_top_topic(raw_doc, tokens, bow) for raw_doc, tokens, bow in zip(eng_raw_docs, docs, comments_corpus)]

        topics = lda.show_topics(formatted=False)
        print(f"Num topics: {num_topics}")
        for topic in topics:
            topic_num = topic[0]
            print(f"Topic number: {topic_num}")
            topic_terms = topic[1]
            for term in topic_terms:
                #print(f"Term: {term[0]}, Translation: {MEANINGS.get(term[0], 'Not Found')}, Probability: {term[1]}")
                print(f"Term: {term[0]}, Probability: {term[1]}")
            
            # print most emblematic comments
            topic_comments = [topic_doc for topic_doc in topic_docs if topic_doc[2] == topic_num]
            topic_comments = [topic_doc for topic_doc in topic_docs if not check_for_repeating_tokens(topic_doc[1])]
            topic_top_comments = sorted(topic_comments, key=lambda tup: tup[3], reverse=True)[:10]
            print("Top comments")
            for topic_top_comment in topic_top_comments:
                print(topic_top_comment[0])

if __name__ == '__main__':
    main()