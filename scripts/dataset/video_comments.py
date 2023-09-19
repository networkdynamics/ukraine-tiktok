import json
import os
import random
import time

import pandas as pd
import tqdm

from pytok.tiktok import PyTok
from pytok import exceptions, utils

def main():

    #hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    video_path = os.path.join(data_dir_path, 'cache', 'related_videos.csv')
    apr_video_path = os.path.join(data_dir_path, 'cache', 'related_apr_videos.csv')
    # video_df = utils.get_video_df(video_path)
    video_df = utils.get_video_df(apr_video_path)
    # video_df = pd.concat([video_df, apr_video_df])
    # video_df = video_df.drop_duplicates(subset=['video_id'])

    comments_dir_path = os.path.join(data_dir_path, "comments")
    if not os.path.exists(comments_dir_path):
        os.mkdir(comments_dir_path)

    chrome_version = 112

    delay = 0
    finished = False

    # while not finished:
        # video_df = video_df.sample(frac=1)
        # try:
    with PyTok(chrome_version=chrome_version, request_delay=delay, headless=False) as api:
        for id, video in tqdm.tqdm(video_df.iterrows(), total=len(video_df), desc='Fetching comments'):

            comment_dir_path = os.path.join(comments_dir_path, video['video_id'])
            if not os.path.exists(comment_dir_path):
                os.mkdir(comment_dir_path)

            comment_file_path = os.path.join(comment_dir_path, f"video_comments.json")

            if os.path.exists(comment_file_path):
                with open(comment_file_path, 'r') as f:
                    comments = json.load(f)
                if len(comments) > 0:
                    all_comments_users = all(isinstance(comment['user'], dict) for comment in comments)

                    all_replies_fetched = True
                    for comment in comments:
                        num_already_fetched = len(comment.get('reply_comment', []) if comment.get('reply_comment', []) is not None else [])
                        num_comments_to_fetch = comment.get('reply_comment_total', 0) - num_already_fetched
                        if num_comments_to_fetch > 0:
                            all_replies_fetched = False

                    if all_replies_fetched and all_comments_users:
                        continue    

            try:
                comments = []
                for comment in api.video(id=video['video_id'], username=video['author_name']).comments(count=1000):
                    comments.append(comment)

                with open(comment_file_path, 'w') as f:
                    json.dump(comments, f)
            except exceptions.NotAvailableException:
                continue

        finished = True

        # except Exception as e:
        #     time.sleep(1800)


if __name__ == '__main__':
    main()