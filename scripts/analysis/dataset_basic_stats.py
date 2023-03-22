import collections
import json
import os

import tqdm
import pandas as pd

import utils

def main():

    comment_df = utils.get_comment_df()
    comment_df = comment_df.drop_duplicates('comment_id')
    video_df = utils.get_video_df()
    video_df = video_df.drop_duplicates('video_id')

    print(f"Num Ukraine invasion related videos: {len(video_df)}")

    print(f"Num comments collected: {len(comment_df)}")

    num_users = len(video_df['user_unique_id'].unique()) 

    print(f"Num users histories collected: {num_users}")


if __name__ == '__main__':
    main()