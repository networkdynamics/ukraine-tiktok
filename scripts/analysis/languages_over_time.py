from datetime import datetime
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import tqdm
import ftlangdetect

def get_language(text):
    try:
        result = ftlangdetect.detect(text)
        return result['lang']
    except Exception as e:
        if str(e) == 'No features in text.':
            return None
        else:
            raise Exception('Unknown error')

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    comment_dir_path = os.path.join(data_dir_path, 'comments')

    comments = []
    for file_name in tqdm.tqdm(os.listdir(comment_dir_path)[:10000]):
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
    comment_df['text'] = comment_df['text'].str.replace(r'\n',  ' ', regex=True)
    comment_df['language'] = comment_df['text'].apply(get_language)

    language_method = 'ru_n_uk'
    time_span = 'broad'

    if language_method == 'top':
        language_count_df = comment_df[['language', 'text']].groupby('language') \
            .count() \
            .rename(columns={'text': 'language_count'}) \
            .reset_index() \
            .sort_values('language_count', ascending=False)
            
        top_languages = language_count_df.head(5)['language'].values.tolist()
        top_languages.append('uk')
        comment_df = comment_df[comment_df['language'].isin(top_languages)]

    elif language_method == 'ukrainian':
        comment_df = comment_df[comment_df['language'].notna()]
        comment_df = comment_df[comment_df['author'].notna()]
        languages = ['uk', 'ru', 'en']
        comment_df = comment_df[comment_df['language'].isin(languages)]

        authors_df = comment_df[['author', 'language']].groupby('author').agg(list).reset_index()
        authors_df = authors_df[authors_df['language'].str.len() > 1]
        authors_df = authors_df[authors_df['language'].apply(lambda langs: 'uk' in langs)]

        comment_df = comment_df.merge(authors_df[['author']], how='inner', on='author')

    elif language_method == 'ru_n_uk':
        languages = ['uk', 'ru']
        comment_df = comment_df[comment_df['language'].isin(languages)]


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

    df = comment_df[['language', 'createtime', 'text']].groupby(['language', pd.Grouper(key='createtime', freq=freq)]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    all_count_df = all_count_df[all_count_df['createtime'] > start_date]
    all_count_df = all_count_df[all_count_df['createtime'] < end_date]

    df = df[df['createtime'] > start_date]
    df = df[df['createtime'] < end_date]

    all_count_df = all_count_df.set_index('createtime')
    df = df.pivot_table(index=['createtime'], columns=['language'], fill_value=0).droplevel(0, axis=1)

    # TODO divide by all counts
    df = df.join(all_count_df)

    language_columns = list(df.columns)
    language_columns.remove('comment_count')
    df = df[language_columns].div(df['comment_count'], axis=0)

    ax = df.plot()
    ax.legend(loc='right')

    fig_dir_path = os.path.join(data_dir_path, '..', 'figs')
    fig_path = os.path.join(fig_dir_path, f'{language_method}_languages_over_time_{time_span}.png')
    plt.savefig(fig_path)

if __name__ == '__main__':
    main()