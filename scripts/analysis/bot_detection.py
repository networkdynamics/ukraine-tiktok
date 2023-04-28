import json
import os

import birdspotter
from birdspotter import BirdSpotter
import numpy as np
import pandas as pd
import tqdm
import xgboost as xgb

from pytok import utils

def get_botness(bs):
    if not hasattr(bs, 'booster'):
        bs.booster = bs.loadPickledBooster(os.path.join(os.path.dirname(birdspotter.__file__), 'data', 'bot_repository_booster.pickle'))
    testdf = bs.featureDataframe.reindex(columns=bs.booster.feature_names)
    test = xgb.DMatrix(testdf.values, feature_names=bs.booster.feature_names)
    bdf = pd.DataFrame()
    bdf['botness'] = bs.booster.predict(test)
    features = bs.booster.predict(test, pred_contribs=True)
    # get top contributing prediction features
    n = 5
    num_users = features.shape[0]
    ind = np.argpartition(features, -n, axis=1)[:, -n:]
    topn = features[np.arange(num_users)[:,None], ind]
    sorted_ind = ind[np.arange(num_users)[:,None], np.argsort(topn)] # sort them
    sorted_topn = features[np.arange(len(sorted_ind))[:,None], sorted_ind]
    bdf['botness_top_features'] = None
    for i, row in bdf.iterrows():
        bdf.loc[i, 'botness_top_features'] = {bs.booster.feature_names[i]: c_prob for i, c_prob in zip(sorted_ind[i], sorted_topn[i])}
    bdf['user_id'] = testdf.index
    __botnessDataframe = bdf.set_index('user_id')
    bs.featureDataframe = bs.featureDataframe.join(__botnessDataframe) 
    bs.featureDataframe = bs.featureDataframe[~bs.featureDataframe.index.duplicated()]
    return bs.featureDataframe

def get_comment(row):
    '%a %b %d %H:%M:%S +0000 %Y'
    comment = {}
    comment['id_str'] = row['comment_id']
    comment['created_at'] = row['createtime'].strftime('%a %b %d %H:%M:%S +0000 %Y')
    comment['text'] = row['text']
    comment['user'] = {
        'id_str': row['author_id'],
        'name': row['author_name'],
        'screen_name': row['nickname'],
        'created_at': row['createtime_user'].strftime('%a %b %d %H:%M:%S +0000 %Y'),
        'description': row['signature'],
        'followers_count': row['followerCount'],
        'friends_count': row['followingCount'],
        'statuses_count': row['videoCount'],
        'favourites_count': row['diggCount'],
        'listed_count': None,
        'profile_image_url_https': None,
        'location': None,
        'verified': row['verified'],
    }
    comment['entities'] = {
        'hashtags': [
            # trying to use a hashtag which isn't used as a feature in the botness classifier
            # 0 hashtags doesn't work with the classifier
            # maybe check if this is robust to multiple hashtags?
            {'text': 'hello'}
        ],
    }
    comment['retweet_count'] = None
    comment['favorite_count'] = row['digg_count']
    comment['source'] = ''
    return comment

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    cache_dir_path = os.path.join(data_dir_path, 'cache')
    all_comments_path = os.path.join(cache_dir_path, 'related_comments.csv')
    comment_path = os.path.join(data_dir_path, 'comments')
    comment_paths = [os.path.join(comment_path, dir_path, 'video_comments.json') for dir_path in os.listdir(comment_path)]

    # get user df
    user_df_path = os.path.join(cache_dir_path, 'all_users.csv')
    if os.path.exists(user_df_path):
        user_df = utils.get_user_df(user_df_path)
    else:
        hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
        searches_dir_path = os.path.join(data_dir_path, 'searches')
        video_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
                + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]
        user_df = utils.get_user_df(user_df_path, file_paths=video_paths+comment_paths)

    comments_df = utils.get_comment_df(all_comments_path, file_paths=comment_paths)
    english_comments_df = comments_df[comments_df['comment_language'] == 'en']

    # format comments for birdspotter
    english_comments_df = english_comments_df.merge(user_df, left_on='author_name', right_on='uniqueId', how='left', suffixes=('', '_user'))

    english_comments_df = english_comments_df[english_comments_df['followingCount'].notna()]
    english_comments_df = english_comments_df.replace({np.nan: None})
    english_comments_df['comment_dict'] = english_comments_df.apply(get_comment, axis=1)

    comments_batch = english_comments_df['comment_dict'].to_list()
    json_path = os.path.join(cache_dir_path, 'all_english_comments.json')
    with open(json_path, 'w') as f:
        json.dump(comments_batch, f)

    bs = BirdSpotter(json_path)
    user_features = get_botness(bs)
    user_features = user_features.merge(user_df, left_on='screen_name', right_on='nickname')
    user_features[['uniqueId', 'botness']].to_csv(os.path.join(cache_dir_path, 'some_users_bot_scores.csv'), index=False)

if __name__ == '__main__':
    main()