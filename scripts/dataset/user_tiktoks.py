import argparse
import json
import os
import random
import time

import tqdm

from TikTokApi import TikTokApi

def main():

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
               + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

    users = set()
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        hashtag_users = set([video['author']['uniqueId'] for video in video_data])
        users = users.union(hashtag_users)

    users_dir_path = os.path.join(data_dir_path, "users")
    if not os.path.exists(users_dir_path):
        os.mkdir(users_dir_path)

    users = list(users)

    delay = 15
    finished = False
    while not finished:
        random.shuffle(users)
        try:
            with TikTokApi(request_delay=delay, headless=True) as api:
                for username in tqdm.tqdm(users):

                    user_dir_path = os.path.join(users_dir_path, username)
                    if not os.path.exists(user_dir_path):
                        os.mkdir(user_dir_path)

                    user_file_path = os.path.join(user_dir_path, f"user_videos.json")
                    if os.path.exists(user_file_path):
                        continue

                    user_videos = []
                    for video in api.user(username=username).videos(count=10000):
                        user_videos.append(video.info())

                    with open(user_file_path, 'w') as f:
                        json.dump(user_videos, f)

                finished = True
        except Exception:
            time.sleep(3600)

if __name__ == '__main__':
    main()
