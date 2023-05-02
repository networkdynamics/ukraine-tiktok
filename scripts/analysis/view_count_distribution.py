import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pytok import utils

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    outputs_dir_path = os.path.join(data_dir_path, 'outputs')
    cache_dir_path = os.path.join(data_dir_path, 'cache')
    related_video_path = os.path.join(cache_dir_path, 'related_videos.csv')
    all_video_path = os.path.join(cache_dir_path, 'all_videos.csv')

    related_video_df = utils.get_video_df(related_video_path)

    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    video_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
            + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]
    all_video_df = utils.get_video_df(all_video_path, file_paths=video_paths)

    related_video_df = related_video_df.merge(all_video_df, on='video_id', how='left')

    # plot view count distribution
    max_view_count = related_video_df['play_count'].max()
    bins = [0] + list(np.logspace(0, np.log10(max_view_count), 20))
    plt.hist(related_video_df['play_count'], bins=bins)
    plt.yscale('symlog')
    plt.xscale('symlog')
    plt.title('View Count Distribution')
    plt.xlabel('View Count')
    plt.ylabel('Number of Videos')
    plt.savefig(os.path.join(outputs_dir_path, 'view_count_distribution.png'))

if __name__ == '__main__':
    main()