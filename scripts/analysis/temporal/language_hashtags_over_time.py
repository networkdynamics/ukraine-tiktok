from datetime import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd
import ftlangdetect

import utils

LANGUAGES = {
    'ru': 'Russian',
    'uk': 'Ukrainian',
    'en': 'English',
    'de': 'German',
    'fr': 'French'
}

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
    data_dir_path = os.path.join(this_dir_path, '..', '..', '..', 'data')
    
    video_df = utils.get_video_df()
    comment_df = utils.get_comment_df()

    video_df['language'] = video_df['desc'].apply(get_language)
    comment_df['language'] = comment_df['text'].apply(get_language)

    language_method = 'russian'
    time_span = 'narrow'

    if language_method == 'russian':
        video_df = video_df[video_df['language'] == 'ru']
        comment_df = comment_df[comment_df['language'] == 'ru']

    if time_span == 'broad':
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 1)
        freq = 'W'
    elif time_span == 'narrow':
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 4, 1)
        freq = 'D'

    all_comment_count_df = comment_df[['createtime', 'text']].groupby(pd.Grouper(key='createtime', freq=freq)) \
        .count() \
        .rename(columns={'text': 'comment_count'}) \
        .reset_index() \
        .sort_values('createtime')

    comment_count_df = comment_df[['language', 'createtime', 'text']].groupby(['language', pd.Grouper(key='createtime', freq=freq)]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    all_video_count_df = comment_df[['createtime', 'text']].groupby(pd.Grouper(key='createtime', freq=freq)) \
        .count() \
        .rename(columns={'text': 'comment_count'}) \
        .reset_index() \
        .sort_values('createtime')

    video_count_df = comment_df[['language', 'createtime', 'text']].groupby(['language', pd.Grouper(key='createtime', freq=freq)]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    all_comment_count_df = all_comment_count_df[all_comment_count_df['createtime'] > start_date]
    all_comment_count_df = all_comment_count_df[all_comment_count_df['createtime'] < end_date]

    comment_count_df = comment_count_df[comment_count_df['createtime'] > start_date]
    comment_count_df = comment_count_df[comment_count_df['createtime'] < end_date]

    all_video_count_df = all_video_count_df[all_video_count_df['createtime'] > start_date]
    all_video_count_df = all_video_count_df[all_video_count_df['createtime'] < end_date]

    video_count_df = video_count_df[video_count_df['createtime'] > start_date]
    video_count_df = video_count_df[video_count_df['createtime'] < end_date]

    all_comment_count_df = all_comment_count_df.set_index('createtime')
    all_video_count_df = all_video_count_df.set_index('createtime')
    comment_count_df = comment_count_df.pivot_table(index=['createtime'], columns=['language'], fill_value=0).droplevel(0, axis=1)
    video_count_df = video_count_df.pivot_table(index=['createtime'], columns=['language'], fill_value=0).droplevel(0, axis=1)

    comment_count_df = comment_count_df.join(all_comment_count_df)
    video_count_df = video_count_df.join(all_video_count_df)

    language_columns = list(comment_count_df.columns)
    language_columns.remove('comment_count')
    comment_count_df = comment_count_df[language_columns].div(comment_count_df['comment_count'], axis=0)
    video_count_df = video_count_df[language_columns].div(video_count_df['comment_count'], axis=0)

    # have nice figure names
    comment_count_df = comment_count_df.rename(columns=LANGUAGES)
    video_count_df = video_count_df.rename(columns=LANGUAGES)

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(video_count_df)
    ax.plot(comment_count_df)
    ax.set_xlabel('Time')
    ax.set_ylabel('Count')
    ax.legend(loc='right')
    plt.tight_layout()

    fig_dir_path = os.path.join(data_dir_path, '..', 'figs')
    fig_path = os.path.join(fig_dir_path, f'{language_method}_languages_over_time_{time_span}.png')
    plt.savefig(fig_path)

if __name__ == '__main__':
    main()