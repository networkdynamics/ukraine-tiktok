import argparse
import json
import os
import time

from pytok import PyTok

def main(args):
    hashtags = ['denazification', 'specialmilitaryoperation', 'africansinukraine', 'putinspeech', 'whatshappeninginukraine', 'greenscreen']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, 'data', 'hashtags')

    if not os.path.exists(data_dir_path):
        os.mkdir(data_dir_path)

    finished = False
    while not finished:
        try:
            with PyTok(chrome_version=args.chrome_version, headless=False) as api:
                for hashtag in hashtags:

                    file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")

                    if os.path.exists(file_path):
                        continue

                    video_data = []
                    for video in api.hashtag(name=hashtag).videos(count=10000):
                        video_data.append(video.info())

                    with open(file_path, 'w') as f:
                        json.dump(video_data, f)

                finished = True
        except Exception:
            time.sleep(600)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--chrome-version')
    args = parser.parse_args()

    main(args)