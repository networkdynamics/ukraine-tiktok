import argparse
import json
import os
import time

from TikTokApi import TikTokApi

def main(args):
    video_data = []

    with TikTokApi() as api:
        for video in api.search.videos(args.search, count=100):
            video_data.append(video.info())

    dir_path = os.path.dirname(args.out_path)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    with open(args.out_path, 'w') as f:
        json.dump(video_data, f)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--search')
    parser.add_argument('--out-path')
    args = parser.parse_args()

    main(args)
