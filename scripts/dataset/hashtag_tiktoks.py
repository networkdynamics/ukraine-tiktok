import argparse
import json
import os
import time

from pytok.tiktok import PyTok

def main():
    #hashtags = ['standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    #hashtags = ['володимирзеленський', 'славаукраїні', 'путінхуйло🔴⚫🇺🇦', 'россия', 
    #'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', 'зеленский', 'путинхуйло']
    hashtags = ['denazification', 'specialmilitaryoperation', 'africansinukraine', 'putinspeech', 'whatshappeninginukraine', 'greenscreen']
    hashtags = ['fyp', 'foryou', 'fypシ', 'viral', 'foryoupage', 'fy', 'edit', 'capcut', 'tiktok', '2022', 'trending', 'funny']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data', 'hashtags')

    #finished = False
    #while not finished:
        #try:
    with PyTok(headless=False) as api:
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