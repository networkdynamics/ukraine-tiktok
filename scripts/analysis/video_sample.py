import datetime
import os

import ftlangdetect
import numpy as np
import pandas as pd

from pytok import utils

def check_english(text):
    try:
        if text is np.nan:
            return False
        result = ftlangdetect.detect(text)
        return result['lang'] == 'en'
    except Exception as e:
        if str(e) == 'No features in text.':
            return False
        else:
            raise Exception('Unknown error')

def main():

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    video_path = os.path.join(data_dir_path, 'cache', 'all_videos.csv')
    video_df = utils.get_video_df(video_path)

    NUM_SAMPLE = 100

    sample_type = 'english_and_invasion'
    if sample_type == 'all':
        video_sample = video_df.sample(NUM_SAMPLE)
    elif sample_type == 'english_and_invasion':
        comment_path = os.path.join(data_dir_path, 'cache', 'all_comments.csv')
        comment_df = utils.get_comment_df(comment_path)
        comment_df['english'] = comment_df['comment_language'] == 'en'
        # get percentage of comments on each video
        video_comments = comment_df[['video_id', 'comment_id', 'english']].groupby('video_id').agg({'english': 'sum', 'comment_id': 'count'})
        video_comments['english_pct'] = video_comments['english'] / video_comments['comment_id']
        
        # join back to videos
        video_sample = video_df.merge(video_comments, how='left', left_on='video_id', right_on='video_id')

        # get vids with english descriptions
        video_sample['english'] = video_sample['desc'].apply(check_english)

        # get vids with at least 50% english comments or english description
        video_sample = video_sample[(video_sample['english_pct'] > 0.5) | (video_sample['english'] == True)]
        # get invasion videos
        video_sample = video_sample[video_sample['createtime'].dt.year == 2022]
        video_sample = video_sample.sample(NUM_SAMPLE)

    sample_path = os.path.join(data_dir_path, 'outputs', f'{sample_type}_video_sample.csv')
    video_sample.to_csv(sample_path)

if __name__ == '__main__':
    main()