from datetime import datetime
import json
import os

import pandas as pd
import tqdm

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    comment_dir_path = os.path.join(data_dir_path, 'comments')

    comments = []
    for file_name in tqdm.tqdm(os.listdir(comment_dir_path)):
        file_path = os.path.join(comment_dir_path, file_name, 'video_comments.json')

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r') as f:
            comment_data = json.load(f)

        comments += comment_data

    comments_data = []
    for comment in comments:
        if isinstance(comment['user'], str):
            author = comment['user']
        elif isinstance(comment['user'], dict):
            if 'unique_id' in comment['user']:
                author = comment['user']['unique_id']
            elif 'uniqueId' in comment['user']:
                author = comment['user']['uniqueId']
            else:
                author = comment['user']['uid']
        else:
            raise Exception()

        comments_data.append((
            datetime.fromtimestamp(comment['create_time']), 
            author, 
            comment['text'],
            comment['aweme_id']
        ))

    comment_df = pd.DataFrame(comments_data, columns=['createtime', 'author', 'text', 'video_id'])

    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
               + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

    videos = []
    for file_path in tqdm.tqdm(file_paths):
        with open(file_path, 'r') as f:
            video_data = json.load(f)
        videos += video_data

    vids_data = [
        (
            video['id'],
            datetime.fromtimestamp(video['createTime']), 
            video['author']['uniqueId'], 
            video['desc'], 
            [challenge['title'] for challenge in video.get('challenges', [])]
        ) 
        for video in videos
    ]

    video_df = pd.DataFrame(vids_data, columns=['id', 'createtime', 'author', 'desc', 'hashtags'])
    video_df = video_df.drop_duplicates('id')

    video_comments_df = video_df.rename(columns={'createtime': 'video_createtime', 'id': 'video_id', 'author': 'video_author', 'desc': 'video_desc', 'hashtags': 'video_hashtags'}) \
        .merge(comment_df.rename(columns={'createtime': 'comment_createtime', 'author': 'comment_author', 'text': 'comment_text'}), on='video_id')

    specific_df = video_comments_df[(video_comments_df['video_hashtags'].apply(lambda hashtags: 'ukraine' in hashtags)) & (video_comments_df['comment_text'].str.contains('tranh'))][['video_desc', 'comment_text']]

    print(specific_df.head())

if __name__ == '__main__':
    main()