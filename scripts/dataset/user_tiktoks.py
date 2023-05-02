import argparse
import json
import os
import random
import time

import tqdm

from pytok.tiktok import PyTok
from pytok import exceptions

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

        hashtag_users = set([(video['author']['uniqueId'],video['author']['id'],video['author']['secUid']) for video in video_data])
        users = users.union(hashtag_users)

    users_dir_path = os.path.join(data_dir_path, "users")
    if not os.path.exists(users_dir_path):
        os.mkdir(users_dir_path)

    chrome_version = os.environ['CHROME_VERSION']

    users = list(users)

    delay = 2
    finished = False
    while not finished:
        random.shuffle(users)
        try:
            with PyTok(request_delay=delay, headless=True, chrome_version=chrome_version) as api:
                for username, user_id, sec_uid in tqdm.tqdm(users):

                    user_dir_path = os.path.join(users_dir_path, username)
                    if not os.path.exists(user_dir_path):
                        os.mkdir(user_dir_path)

                    user_file_path = os.path.join(user_dir_path, f"user_videos.json")
                    if os.path.exists(user_file_path):
                        continue

                    user_videos = []
                    try:
                        for video in api.user(username=username, user_id=user_id, sec_uid=sec_uid).videos(count=10000):
                            user_videos.append(video.info())
                    except exceptions.NotAvailableException:
                        continue
                    except exceptions.CaptchaException:
                        raise

                    with open(user_file_path, 'w') as f:
                        json.dump(user_videos, f)

                finished = True
        except exceptions.TimeoutException:
            time.sleep(3600)

if __name__ == '__main__':
    main()
