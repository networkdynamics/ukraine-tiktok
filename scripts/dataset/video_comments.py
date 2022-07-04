import argparse
from csv import excel
import json
import os
import random
import time

import tqdm

from TikTokApi import TikTokApi

def main():

    hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    videos = []
    for hashtag in hashtags:
        print(f"Getting hashtag users: {hashtag}")
        file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data

    comments_dir_path = os.path.join(data_dir_path, "comments")
    if not os.path.exists(comments_dir_path):
        os.mkdir(comments_dir_path)

    delay = 2
    finished = False

    while not finished:
        random.shuffle(videos)
        try:
            with TikTokApi(request_delay=delay, headless=True) as api:
                for video in tqdm.tqdm(videos):

                    comment_dir_path = os.path.join(comments_dir_path, video['id'])
                    if not os.path.exists(comment_dir_path):
                        os.mkdir(comment_dir_path)

                    comment_file_path = os.path.join(comment_dir_path, f"video_comments.json")
                    if os.path.exists(comment_file_path):
                        continue

                    comments = []
                    for comment in api.video(id=video['id'], username=video['author']['uniqueId']).comments(count=1000):
                        comments.append(comment)

                    with open(comment_file_path, 'w') as f:
                        json.dump(comments, f)
                finished = True
        except Exception:
            time.sleep(1800)


if __name__ == '__main__':
    main()