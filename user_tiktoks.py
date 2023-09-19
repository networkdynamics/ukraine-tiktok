import argparse
import json
import os
import random
import time

import tqdm

from pytok import PyTok
from pytok import exceptions

def main(args):

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, 'data')

    videos_dir_path = os.path.join(data_dir_path, 'videos')
    video_paths = [os.path.join(videos_dir_path, file_name) for file_name in os.listdir(videos_dir_path)]

    users = set()
    for video_path in video_paths:
        file_path = os.path.join(video_path, 'video_data.json')
        with open(file_path, 'r') as f:
            video = json.load(f)

        hashtag_user = (video['author']['uniqueId'],video['author']['id'],video['author']['secUid'])
        users = users.add(hashtag_user)

    users_dir_path = os.path.join(data_dir_path, "users")
    if not os.path.exists(users_dir_path):
        os.mkdir(users_dir_path)

    users = list(users)

    delay = 2
    finished = False
    while not finished:
        random.shuffle(users)
        try:
            with PyTok(request_delay=delay, headless=True, chrome_version=args.chrome_version) as api:
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
        except Exception:
            raise

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--chrome-version')
    args = parser.parse_args()

    main(args)
