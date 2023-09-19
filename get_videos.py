import argparse
import json
import os
import random
import time

import pandas as pd
import tqdm

from pytok import PyTok, exceptions

def main(args):
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    video_df = pd.read_csv(os.path.join(this_dir_path, 'video_ids.csv'), dtype={'video_id': str, 'user_unique_id': str})

    data_dir_path = os.path.join(this_dir_path, 'data')

    if not os.path.exists(data_dir_path):
        os.mkdir(data_dir_path)

    videos_dir_path = os.path.join(data_dir_path, 'videos')

    if not os.path.exists(videos_dir_path):
        os.mkdir(videos_dir_path)

    videos = [{
        'id': row['video_id'],
        'author_id': row['user_unique_id']
    } for idx, row in video_df.iterrows()]

    delay = 0
    backoff_delay = 1800
    finished = False

    while not finished:
        random.shuffle(videos)
        try:
            with PyTok(chrome_version=args.chrome_version, request_delay=delay, headless=True) as api:
                for video in tqdm.tqdm(videos):

                    video_dir_path = os.path.join(videos_dir_path, video['id'])
                    if not os.path.exists(video_dir_path):
                        os.mkdir(video_dir_path)

                    video_file_path = os.path.join(video_dir_path, f"video_data.json")
                    if os.path.exists(video_file_path):
                        continue

                    try:
                        video_data = api.video(id=video['id'], username=video['author_id']).info_full()

                        with open(video_file_path, 'w') as f:
                            json.dump(video_data, f)
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