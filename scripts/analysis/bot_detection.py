import json
import os

from birdspotter import BirdSpotter
import pandas as pd

from pytok import utils

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    cache_dir_path = os.path.join(data_dir_path, 'cache')

    # get user df
    user_df_path = os.path.join(cache_dir_path, 'all_users.csv')
    if os.path.exists(user_df_path):
        user_df = pd.read_csv(user_df_path)
    else:
        comment_path = os.path.join(data_dir_path, 'comments')
        comment_paths = [os.path.join(comment_path, dir_path, 'video_comments.json') for dir_path in os.listdir(comment_path)]
        hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
        searches_dir_path = os.path.join(data_dir_path, 'searches')
        video_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
                + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]
        # user_df = utils.get_user_df(user_df_path, file_paths=video_paths+comment_paths)

    english_comments_path = os.path.join(cache_dir_path, 'all_english_comments.csv')
    english_comments_df = pd.read_csv(english_comments_path)

    # format comments for birdspotter
    # english_comments_df = english_comments_df.merge(user_df, left_on='comment_author_id', right_on='user_id', how='left')

    comments = []
    for _, row in english_comments_df.iterrows():
        comment = {}
        comment['id_str'] = row['comment_id']
        comment['created_at'] = row['createtime']
        comment['text'] = row['text']
        comment['user'] = {
            'id_str': row['author_id'],
            'name': row['author_name'],
            'screen_name': row['author_name'],
            'created_at': None, # row['user_createtime'],# TODO get from file
            'description': None, # row['user_desc'],
            'followers_count': None, #row['user_followers_count'],
            'friends_count': None #row['user_following_count']
        }
        comment['entities'] = {
            'hashtags': [],
        }
        comment['retweet_count'] = None
        comment['favorite_count'] = None
        comments.append(comment)

    json_path = os.path.join(cache_dir_path, 'all_english_comments.jsonl')
    with open(json_path, 'w') as f:
        json.dump(comments, f, indent=4)

    bs = BirdSpotter(json_path)
    bot_scores = bs.getLabeledUsers()

    # save to csv
    bot_scores_path = os.path.join(cache_dir_path, 'all_english_comments_bot_scores.csv')
    english_comments_df[['comment_id', 'bot_score']].to_csv(bot_scores_path)

if __name__ == '__main__':
    main()