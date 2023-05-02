from datetime import datetime
import collections
import json
import os
import re

from matplotlib import pyplot as plt
import pandas as pd
import tqdm

import utils

def main():

    #file_hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3' \
    #    'володимирзеленський', 'славаукраїні', 'путінхуйло🔴⚫🇺🇦', 'россия', 'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', \
    #    'зеленский', 'путинхуйло', 'denazification', 'specialmilitaryoperation', 'africansinukraine', 'putinspeech', 'whatshappeninginukraine']

    NUM_TOP_HASHTAGS = 5

    video_df = utils.get_video_df()

    hashtags_df = video_df.explode('hashtags')

    filter_method = 'top'
    if filter_method == 'top':
        top_hashtags_df = hashtags_df.groupby('hashtags')['desc'].count().sort_values(ascending=False).head(NUM_TOP_HASHTAGS)
        top_hashtags = set(top_hashtags_df.index)

        filtered_hashtags_df = hashtags_df[hashtags_df['hashtags'].isin(top_hashtags)]

    elif filter_method == 'russiavsukraine':
        russiavukraine_words = ['зеленский', 'путинхуйло', 'зеленський', 'путінхуйло🔴⚫🇺🇦']
        russiavukraine = [f"{word}" for word in russiavukraine_words]
        filtered_hashtags_df = hashtags_df[hashtags_df['hashtags'].isin(russiavukraine)]

    all_count_df = video_df[['createtime', 'desc']].groupby(pd.Grouper(key='createtime', freq='W')) \
        .count() \
        .rename(columns={'desc': 'video_count'}) \
        .reset_index() \
        .sort_values('createtime')

    df = filtered_hashtags_df[['hashtags', 'createtime', 'desc']].groupby(['hashtags', pd.Grouper(key='createtime', freq='W')]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 1)

    all_count_df = all_count_df[all_count_df['createtime'] > start_date]
    all_count_df = all_count_df[all_count_df['createtime'] < end_date]

    df = df[df['createtime'] > start_date]
    df = df[df['createtime'] < end_date]

    all_count_df = all_count_df.set_index('createtime')
    df = df.pivot_table(index=['createtime'], columns=['hashtags'], fill_value=0).droplevel(0, axis=1)

    # TODO divide by all counts
    df = df.join(all_count_df)

    hashtag_columns = list(df.columns)
    hashtag_columns.remove('video_count')
    df = df[hashtag_columns].div(df['video_count'], axis=0)

    df.plot()

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..', '..')
    outputs_dir_path = os.path.join(root_dir_path, 'data', 'outputs')
    fig_dir_path = os.path.join(root_dir_path, 'figs')

    filename = f'{filter_method}_hashtags_over_time'
    fig_path = os.path.join(fig_dir_path, f"{filename}.png")
    plt.savefig(fig_path)

    df.to_csv(os.path.join(outputs_dir_path, f"{filename}.csv"))


if __name__ == '__main__':
    main()