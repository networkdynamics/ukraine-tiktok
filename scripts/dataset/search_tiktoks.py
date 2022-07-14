import argparse
import json
import os

from TikTokApi import TikTokApi

def main():
    keywords = ['ukraine']
    video_data = []

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data', 'searches')

    for keyword in keywords:
        with TikTokApi() as api:
            for video in api.search(keyword).videos(count=100):
                video_data.append(video.info())

        file_path = os.path.join(data_dir_path, f"{keyword}_videos.json")
        with open(file_path, 'w') as f:
            json.dump(video_data, f)

if __name__ == '__main__':
    main()
