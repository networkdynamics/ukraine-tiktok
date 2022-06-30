import argparse
import json
import os

from TikTokApi import TikTokApi

def main():
    hashtags = ['standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    with TikTokApi() as api:
        for hashtag in hashtags:

            video_data = []
            for video in api.hashtag(name=hashtag).videos(count=10000):
                video_data.append(video.info())

            file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")
            with open(file_path, 'w') as f:
                json.dump(video_data, f)

if __name__ == '__main__':
    main()