import json
import os
import random
import time

import tqdm

from TikTokApi import TikTokApi
from TikTokApi import exceptions

def main():

    #hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
               + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

    videos = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data


    comments_dir_path = os.path.join(data_dir_path, "comments")
    if not os.path.exists(comments_dir_path):
        os.mkdir(comments_dir_path)

    blacklist_hashtags = ['derealization']

    chrome_version = int(os.environ['CHROME_VERSION'])

    delay = 0
    finished = False

    while not finished:
        random.shuffle(videos)
        try:
            with TikTokApi(chrome_version=chrome_version, request_delay=delay, headless=True) as api:
                for video in tqdm.tqdm(videos):

                    hashtags = [challenge['title'] for challenge in video.get('challenges', [])]
                    if any(blacklist_hashtag in hashtags for blacklist_hashtag in blacklist_hashtags):
                        continue

                    comment_dir_path = os.path.join(comments_dir_path, video['id'])
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
                        for comment in api.video(id=video['id'], username=video['author']['uniqueId']).comments(count=1000):
                            comments.append(comment)

                        with open(comment_file_path, 'w') as f:
                            json.dump(comments, f)
                    except exceptions.NotAvailableException:
                        continue

                finished = True

        except Exception as e:
            time.sleep(1800)


if __name__ == '__main__':
    main()