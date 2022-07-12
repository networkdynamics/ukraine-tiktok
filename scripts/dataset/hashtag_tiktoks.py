import argparse
import json
import os
import time

from TikTokApi import TikTokApi

def main():
    #hashtags = ['standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    hashtags = ['володимирзеленський', 'славаукраїні', 'путінхуйло', 'россия', 
    'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', 'зеленский', 'путинхуйло']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    #finished = False
    #while not finished:
        #try:
    with TikTokApi(headless=True) as api:
        for hashtag in hashtags:

            file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")

            if os.path.exists(file_path):
                continue

            video_data = []
            for video in api.hashtag(name=hashtag).videos(count=10000):
                video_data.append(video.info())

            with open(file_path, 'w') as f:
                json.dump(video_data, f)

                #finished = True
        #except Exception:
            #time.sleep(600)

if __name__ == '__main__':
    main()