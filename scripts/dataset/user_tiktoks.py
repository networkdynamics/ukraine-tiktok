import argparse
import json
import os
import random
import time

import tqdm

from TikTokApi import TikTokApi

def main():

    hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    users = set()
    for hashtag in hashtags:
        print(f"Getting hashtag users: {hashtag}")
        file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        hashtag_users = set([video['author']['uniqueId'] for video in video_data])
        users = users.union(hashtag_users)

    users_dir_path = os.path.join(data_dir_path, "users")
    if not os.path.exists(users_dir_path):
        os.mkdir(users_dir_path)

    users = list(users)

    delay = 10
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
            time.sleep(600)

if __name__ == '__main__':
    main()
