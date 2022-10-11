from datetime import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd

import utils

def get_df(file_name):
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    top_dir_path = os.path.join(this_dir_path, '..', '..')
    outputs_dir_path = os.path.join(top_dir_path, 'data', 'outputs')
    df = pd.read_csv(os.path.join(outputs_dir_path, file_name))
    df['createtime'] = pd.to_datetime(df['createtime'])
    df = df.set_index('createtime')
    return df

def plot_events(axes, events):
    for ax in axes:
        for event in events:
            ax.axvline(x=event[0])

    for event in events:
        axes[-1].text(event[0], 0.4, event[1], rotation=45)

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    top_dir_path = os.path.join(this_dir_path, '..', '..')
    fig_dir_path = os.path.join(top_dir_path, 'figs')
    outputs_dir_path = os.path.join(top_dir_path, 'data', 'outputs')

    fig, axes = plt.subplots(nrows=6, ncols=1, sharex=True, figsize=(10, 20))

    comment_df = utils.get_comment_df()
    comment_count_df = comment_df[['createtime', 'text']].groupby(pd.Grouper(key='createtime', freq='W')) \
        .count() \
        .sort_values('createtime') \
        .rename(columns={'text': 'Comment Count'})

    video_df = utils.get_video_df()
    video_count_df = video_df[['createtime', 'desc']].groupby(pd.Grouper(key='createtime', freq='W')) \
        .count() \
        .sort_values('createtime') \
        .rename(columns={'desc': 'Video Count'})

    comment_count_df.plot(ax=axes[0])
    video_count_df.plot(ax=axes[0])
    axes[0].set_ylabel('Count')
    axes[0].set_title('Count of Comments and Videos')
    axes[0].legend(loc='right')

    top_hashtags_df = get_df('top_hashtags_over_time.csv')
    top_hashtags_df.plot(ax=axes[1])
    axes[1].set_ylabel('Share')
    axes[1].set_title('Top 5 Hashtag Counts')
    axes[1].legend(loc='right')

    top_languages_df = get_df('top_languages_over_time_broad.csv')
    top_languages_df.plot(ax=axes[2])
    axes[2].set_ylabel('Share')
    axes[2].set_title('Top 6 Language Counts')
    axes[2].legend(loc='right')

    ukrainian_languages_df = get_df('ukrainian_languages_over_time_broad.csv')
    ukrainian_languages_df.plot(ax=axes[3])
    axes[3].set_ylabel('Share')
    axes[3].set_title('Language use of Users who have made at least one Comment in Ukrainian')
    axes[3].legend(loc='right')

    country_words_df = get_df('countries_words_over_time_broad.csv')
    country_words_df.plot(ax=axes[4])
    axes[4].set_ylabel('Share')
    axes[4].set_title('Country Mentions Count')
    axes[4].legend(loc='right')

    leader_words_df = get_df('leaders_words_over_time_broad.csv')
    leader_words_df.plot(ax=axes[5])
    axes[5].set_ylabel('Share')
    axes[5].set_xlabel('Time')
    axes[5].set_title('Leader Mentions Count')
    axes[5].legend(loc='right')

    events = [
        (datetime(2022, 1, 17), 'Russia evacuates its Embassy in Kyiv'),
        (datetime(2022, 2, 23), 'Russia invades Ukraine')
    ]
    plot_events(axes, events)

    plt.tight_layout()

    fig_path = os.path.join(fig_dir_path, f'all_over_time.png')
    plt.savefig(fig_path)

if __name__ == '__main__':
    main()