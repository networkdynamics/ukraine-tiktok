import argparse
import json
import os
import time

import tqdm

from TikTokApi import TikTokApi

def main(args):

    with open(args.in_path, 'r') as f:
        video_data = json.load(f)

    users = list(set([video['author']['uniqueId'] for video in video_data]))

    user_videos = []

    with TikTokApi() as api:
        for username in tqdm.tqdm(users):
            for video in api.user(username=username).videos(count=1000):
                user_videos.append(video.info())

    dir_path = os.path.dirname(args.out_path)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    with open(args.out_path, 'w') as f:
        json.dump(video_data, f)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--in-path')
    parser.add_argument('--out-path')
    args = parser.parse_args()

    main(args)
