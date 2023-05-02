import collections
import json
import os

import tqdm
import pandas as pd

from pytok import utils

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    cache_dir_path = os.path.join(data_dir_path, 'cache')
    related_videos_path = os.path.join(cache_dir_path, 'related_videos.csv')

    video_df = utils.get_video_df(related_videos_path)

    related_comments_path = os.path.join(cache_dir_path, 'related_comments.csv')
    if not os.path.exists(related_comments_path):
        all_comments_path = os.path.join(cache_dir_path, 'all_comments.csv')
        comment_path = os.path.join(data_dir_path, 'comments')
        comment_paths = [os.path.join(comment_path, dir_path, 'video_comments.json') for dir_path in os.listdir(comment_path)]
        comment_df = utils.get_comment_df(all_comments_path, file_paths=comment_paths)

        # get comments where video is in related videos
        comment_df = comment_df[comment_df['video_id'].isin(video_df['video_id'])]

        comment_df.to_csv(related_comments_path, index=False)
    else:
        comment_df = utils.get_comment_df(related_comments_path)

    print(f"Num Ukraine invasion related videos: {len(video_df)}")

    print(f"Num comments collected: {len(comment_df)}")

    num_users = len(set(video_df['author_id'].unique()).union(set(comment_df['author_id'].unique())))

    print(f"Num users: {num_users}")


if __name__ == '__main__':
    main()