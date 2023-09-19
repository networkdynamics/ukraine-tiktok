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

    videos = []
    for video_path in video_paths:
        file_path = os.path.join(video_path, 'video_data.json')
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos.append(video_data)

    delay = 0
    backoff_delay = 1800
    finished = False

    while not finished:
        random.shuffle(videos)
        try:
            with PyTok(chrome_version=args.chrome_version, request_delay=delay, headless=True) as api:
                for video in tqdm.tqdm(videos):

                    comment_dir_path = os.path.join(videos_dir_path, video['id'])
                    if not os.path.exists(comment_dir_path):
                        os.mkdir(comment_dir_path)

                    comment_file_path = os.path.join(comment_dir_path, f"video_comments.json")
                    if os.path.exists(comment_file_path):
                        continue

                    try:
                        comments = []
                        for comment in api.video(id=video['id'], username=video['author']['uniqueId']).comments(count=1000):
                            comments.append(comment)

                        with open(comment_file_path, 'w') as f:
                            json.dump(comments, f)
                    except exceptions.NotAvailableException:
                        continue

                finished = True

        except exceptions.TimeoutException as e:
            time.sleep(backoff_delay)
        except Exception:
            raise


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--chrome-version', type=int, default=104)
    args = parser.parse_args()

    main(args)