import argparse
import json
import os

import tqdm

from TikTokApi import TikTokApi

def main():
    keywords = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3' \
    'володимирзеленський', 'славаукраїні', 'путінхуйло🔴⚫🇺🇦', 'россия', 'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', \
    'зеленский', 'путинхуйло', '%23denazification', '%23specialmilitaryoperation', '%23africansinukraine', '%23putinspeech', '%23whatshappeninginukraine']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data', 'searches')

    for keyword in keywords:
        file_path = os.path.join(data_dir_path, f"{keyword}_videos.json")
        if os.path.exists(file_path):
            continue

        video_data = []
        with TikTokApi() as api:
            for video in tqdm.tqdm(api.search(keyword).videos(count=10000), total=10000):
                video_data.append(video.info())

        with open(file_path, 'w') as f:
            json.dump(video_data, f)

if __name__ == '__main__':
    main()
