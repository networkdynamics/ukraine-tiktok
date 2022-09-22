from datetime import datetime
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import tqdm
import ftlangdetect

def where_contains_words(df, words):
    subset_dfs = []
    for word in words:
        regex = rf"\b{word}\b"
        subset_df = df[df['text'].str.contains(regex, case=False)]
        subset_df['word'] = word
        subset_dfs.append(subset_df)

    return pd.concat(subset_dfs)

def load_df():
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
    comment_df = comment_df[comment_df['text'].notna()]
    comment_df['text'] = comment_df['text'].str.replace(r'\n',  ' ', regex=True)
    return comment_df

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    df_cache_path = os.path.join(data_dir_path, 'cache', 'all_comments.csv')

    if os.path.exists(df_cache_path):
        comment_df = pd.read_csv(df_cache_path)
        comment_df = comment_df[comment_df['text'].notna()]
        comment_df['createtime'] = pd.to_datetime(comment_df['createtime'])
    else:
        comment_df = load_df()
        comment_df.to_csv(df_cache_path)

    word_method = 'leaders'
    time_span = 'broad'

    if word_method == 'countries':
        countries = ['russia', 'ukraine', 'usa', 'united states', 'uk', 'united kingdom', 'france', 'germany']
        comment_df = where_contains_words(comment_df, countries)

    elif word_method == 'leaders':
        leaders = ['putin', 'zelensky', 'zelenskyy', 'zelenskiy', 'boris', 'biden', 'trump', 'macron', 'scholz', 'merkel']
        comment_df = where_contains_words(comment_df, leaders)


    if time_span == 'broad':
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 1)
        freq = 'W'
    elif time_span == 'narrow':
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 4, 1)
        freq = 'D'

    all_count_df = comment_df[['createtime', 'text']].groupby(pd.Grouper(key='createtime', freq=freq)) \
        .count() \
        .rename(columns={'text': 'comment_count'}) \
        .reset_index() \
        .sort_values('createtime')

    df = comment_df[['word', 'createtime', 'text']].groupby(['word', pd.Grouper(key='createtime', freq=freq)]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    all_count_df = all_count_df[all_count_df['createtime'] > start_date]
    all_count_df = all_count_df[all_count_df['createtime'] < end_date]

    df = df[df['createtime'] > start_date]
    df = df[df['createtime'] < end_date]

    all_count_df = all_count_df.set_index('createtime')
    df = df.pivot_table(index=['createtime'], columns=['word'], fill_value=0).droplevel(0, axis=1)

    # TODO divide by all counts
    df = df.join(all_count_df)

    word_columns = list(df.columns)
    word_columns.remove('comment_count')
    df = df[word_columns].div(df['comment_count'], axis=0)

    ax = df.plot()
    ax.legend(loc='right')

    fig_dir_path = os.path.join(data_dir_path, '..', 'figs')
    fig_path = os.path.join(fig_dir_path, f'{word_method}_words_over_time_{time_span}.png')
    plt.savefig(fig_path)

if __name__ == '__main__':
    main()