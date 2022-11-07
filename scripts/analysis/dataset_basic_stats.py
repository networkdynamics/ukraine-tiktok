import collections
import json
import os

import tqdm
import pandas as pd


def main():

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    
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
    print(f"Num Ukraine invasion related videos: {len(video_ids)}")

    comment_dir_path = os.path.join(data_dir_path, 'comments')

    num_comments = 0
    for file_name in tqdm.tqdm(os.listdir(comment_dir_path)):
        file_path = os.path.join(comment_dir_path, file_name, 'video_comments.json')

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r') as f:
            comments = json.load(f)

        num_comments += len(comments)
        num_comments += sum(len(comment.get('reply_comment', []) if comment.get('reply_comment', []) else []) for comment in comments)

    print(f"Num comments collected: {num_comments}")

    user_dir_path = os.path.join(data_dir_path, 'users')

    num_users_histories = len(video_ids['user_unique_id'].unique())

    print(f"Num users histories collected: {num_users_histories}")


if __name__ == '__main__':
    main()