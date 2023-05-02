import collections
import json
import os

import pandas as pd


def main():

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    dataset_path = os.path.join(data_dir_path, 'dataset')
    if not os.path.exists(dataset_path):
        os.mkdir(dataset_path)
    
    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
               + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

    blacklist_hashtags = ['derealization']

    video_ids = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        for video in video_data:
            hashtags = [challenge['title'] for challenge in video.get('challenges', [])]
            if any(blacklist_hashtag in hashtags for blacklist_hashtag in blacklist_hashtags):
                continue
            video_ids.append((video['id'], video['author']['uniqueId']))

    video_ids = pd.DataFrame(video_ids, columns=['video_id', 'user_unique_id'])
    video_ids = video_ids.drop_duplicates()
    video_ids.to_csv(os.path.join(dataset_path, 'video_ids.csv'), index=False)


if __name__ == '__main__':
    main()