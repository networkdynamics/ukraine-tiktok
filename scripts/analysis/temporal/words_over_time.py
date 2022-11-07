from datetime import datetime
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import tqdm
import ftlangdetect

import utils

def where_contains_words(df, words):
    subset_dfs = []
    for word in words:
        for word_option in words[word]:
            regex = rf"\b{word_option}\b"
            subset_df = df[df['text'].str.contains(regex, case=False)]
            subset_df['word'] = word
            subset_dfs.append(subset_df)

    return pd.concat(subset_dfs)


def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', '..', 'data')

    comment_df = utils.get_comment_df()

    word_method = 'leaders'
    time_span = 'broad'

    if word_method == 'countries':
        countries = {
            'Russia': ['russia'],
            'Ukraine': ['ukraine'],
            'US': ['usa', 'united states', 'the us'],
            'UK': ['uk', 'united kingdom'],
            'France': ['france'],
            'Germany': ['germany']
        }
        comment_df = where_contains_words(comment_df, countries)

    elif word_method == 'leaders':
        leaders = {
            'Putin': ['putin'], 
            'Zelensky': ['zelensky', 'zelenskyy', 'zelenskiy'],
            'Johnson': ['boris'],
            'Biden': ['biden'], 
            'Trump': ['trump'], 
            'Macron': ['macron']
        }
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
    output_name = f'{word_method}_words_over_time_{time_span}'
    fig_path = os.path.join(fig_dir_path, f"{output_name}.png")
    plt.savefig(fig_path)

    df.to_csv(os.path.join(data_dir_path, 'outputs', f"{output_name}.csv"))

if __name__ == '__main__':
    main()