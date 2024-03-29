from datetime import datetime
import json
import os
import re

import pandas as pd
import tqdm

def get_comment_features(comment):
    comment_user = comment['user']
    if isinstance(comment_user, str):
        raise ValueError()
    elif isinstance(comment_user, dict):
        if 'unique_id' in comment_user:
            author_id = comment_user['uid']
            author_name = comment_user['unique_id']
        elif 'uniqueId' in comment_user:
            author_id = comment_user['id']
            author_name = comment_user['uniqueId']
        else:
            author_name = ''
            author_id = comment_user['uid']
    else:
        raise ValueError()

    mentioned_users = [info['user_id'] for info in comment['text_extra'] if info['user_id'] != '']

    return author_id, author_name, mentioned_users

def load_comment_df():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    comment_dir_path = os.path.join(data_dir_path, 'comments')

    comments_data = []
    for file_name in tqdm.tqdm(os.listdir(comment_dir_path)):
        file_path = os.path.join(comment_dir_path, file_name, 'video_comments.json')

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r') as f:
            comments = json.load(f)

        for comment in comments:

            try:
                author_id, author_name, mentioned_users = get_comment_features(comment)
            except ValueError:
                continue

            comment_replies = comment.get('reply_comment', None)
            if comment_replies:
                for reply_comment in comment_replies:
                    try:
                        reply_author_id, reply_author_name, reply_mentioned_users = get_comment_features(reply_comment)
                    except ValueError:
                        continue

                    comments_data.append((
                        reply_comment['cid'],
                        datetime.fromtimestamp(reply_comment['create_time']), 
                        reply_author_name,
                        reply_author_id, 
                        reply_comment['text'],
                        reply_mentioned_users,
                        reply_comment['aweme_id'],
                        reply_comment['comment_language'],
                        comment['cid']
                    ))

            comments_data.append((
                comment['cid'],
                datetime.fromtimestamp(comment['create_time']), 
                author_name,
                author_id, 
                comment['text'],
                mentioned_users,
                comment['aweme_id'],
                comment['comment_language'],
                None
            ))

    comment_df = pd.DataFrame(comments_data, columns=['comment_id', 'createtime', 'author_name', 'author_id', 'text', 'mentions', 'video_id', 'comment_language', 'reply_comment_id'])
    comment_df = comment_df[comment_df['text'].notna()]
    comment_df = comment_df[comment_df['video_id'].notna()]
    comment_df = comment_df[comment_df['mentions'].notna()]
    comment_df['text'] = comment_df['text'].str.replace(r'\n',  ' ', regex=True)
    comment_df = comment_df.drop_duplicates('comment_id')
    return comment_df

def get_comment_df():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    df_cache_path = os.path.join(data_dir_path, 'cache', 'all_comments.csv')

    if os.path.exists(df_cache_path):
        comment_df = pd.read_csv(df_cache_path, dtype={'author_name': str, 'author_id': str, 'comment_id': str, 'video_id': str, 'reply_comment_id': str})
        comment_df = comment_df[comment_df['text'].notna()]
        comment_df = comment_df[comment_df['video_id'].notna()]
        comment_df = comment_df[comment_df['mentions'].notna()]
        comment_df['mentions'] = comment_df['mentions'].apply(str_to_list)
        comment_df['createtime'] = pd.to_datetime(comment_df['createtime'])
    else:
        comment_df = load_comment_df()
        comment_df.to_csv(df_cache_path)

    return comment_df


def str_to_list(stri):
    if ',' not in stri:
        return []
    return [word.strip()[1:-1] for word in stri[1:-1].split(',')]

def get_video_df():

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..')
    data_dir_path = os.path.join(root_dir_path, 'data')

    video_df_path = os.path.join(data_dir_path, 'cache', 'all_videos.csv')

    if os.path.exists(video_df_path):
        video_df = pd.read_csv(video_df_path, \
            dtype={'author_name': str, 'author_id': str, 'video_id': str, 'share_video_id': str, 'share_video_user_id': str})
        video_df['createtime'] = pd.to_datetime(video_df['createtime'])
        video_df['mentions'] = video_df['mentions'].apply(str_to_list)
        video_df['hashtags'] = video_df['hashtags'].apply(str_to_list)
        video_df['desc'] = video_df['desc'].fillna('')
        return video_df

    else:
        hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
        searches_dir_path = os.path.join(data_dir_path, 'searches')
        file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
                + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

        videos = []
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                video_data = json.load(f)

            videos += video_data

        vids_data = []
        for video in videos:
            # get text extra relating to user names
            video_mentions = [extra for extra in video.get('textExtra', []) if extra['userId'] != '']

            # get all reply types
            match = re.search("^\#([^# ]+) [^@# ]+ @([^ ]+)", video['desc'])
            if match and len(video_mentions) > 0:
                # if there are multiple mentions we get the first
                if video_mentions[0]['awemeId'] != '':
                    share_video_id = video_mentions[0]['awemeId']
                elif video['duetInfo']['duetFromId'] != '0':
                    share_video_id = video['duetInfo']['duetFromId']
                else:
                    # no way to get shared video id
                    share_video_id = None
                
                share_video_user_id = video_mentions[0]['userId']
                share_video_user_name = video_mentions[0]['userUniqueId']
                share_type = match.group(1)

                video_mentions = video_mentions[1:]
            else:
                share_video_id = None
                share_video_user_id = None
                share_video_user_name = None
                share_type = None

            # get duets that we didn't get with the regex
            if video['duetInfo']['duetFromId'] != '0' and not share_video_id:
                duet_infos = [mention for mention in video_mentions if mention['awemeId'] == video['duetInfo']['duetFromId']]
                # sometimes the awemeId is missing
                if duet_infos:
                    duet_info = duet_infos[0]
                    share_video_id = duet_info['awemeId']
                else:
                    duet_info = video_mentions[0]
                    share_video_id = video['duetInfo']['duetFromId']
                
                share_video_user_id = duet_info['userId']
                share_video_user_name = duet_info['userUniqueId']
                share_type = 'duet'

                video_mentions = [mention for mention in video_mentions if mention['awemeId'] != video['duetInfo']['duetFromId']]

            # get user mentions
            mentions = []
            if len(video_mentions) > 0:
                mentions = [mention['userId'] for mention in video_mentions]

            if video['duetInfo']['duetFromId'] != '0' and share_video_id and video['duetInfo']['duetFromId'] != share_video_id:
                raise ValueError("Comment metadata is mismatched")

            vids_data.append((
                video['id'],
                datetime.fromtimestamp(video['createTime']), 
                video['author']['uniqueId'], 
                video['author']['id'],
                video['desc'], 
                [challenge['title'] for challenge in video.get('challenges', [])],
                share_video_id,
                share_video_user_id,
                share_video_user_name,
                share_type,
                mentions
            ))

        video_df = pd.DataFrame(vids_data, columns=[
            'video_id', 'createtime', 'author_name', 'author_id', 'desc', 'hashtags',
            'share_video_id', 'share_video_user_id', 'share_video_user_name', 'share_type', 'mentions'
        ])
        video_df = video_df[video_df['desc'].notna()]
        video_df = video_df.drop_duplicates('video_id')
        video_df.to_csv(video_df_path)
        return video_df