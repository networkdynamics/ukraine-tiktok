from datetime import datetime
import json
import os

import networkx as nx
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
            comment['id'],
            datetime.fromtimestamp(comment['create_time']), 
            author, 
            comment['text'],
            comment['aweme_id']
        ))

    comment_df = pd.DataFrame(comments_data, columns=['id', 'createtime', 'author', 'text', 'video_id'])
    count_comments_df = comment_df.groupby('author')[['createtime']].count().reset_index().rename(columns={'createtime': 'comment_count'})

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
    count_vids_df = video_df.groupby('author')[['createtime']].count().reset_index().rename(columns={'createtime': 'video_count'})

    counts_df = count_vids_df.merge(count_comments_df, how='outer', on='author')

    print(f"Number of users captured: {len(counts_df)}")
    print(f"Number of users who posted a video and no comment: {len(counts_df[(counts_df['comment_count'].isnull()) & (counts_df['video_count'] > 0)])}")
    print(f"Number of users who posted a comment and no video: {len(counts_df[(counts_df['comment_count'] > 0) & (counts_df['video_count'].isnull())])}")
    print(f"Number of users who posted a comment and posted a video: {len(counts_df[(counts_df['comment_count'] > 0) & (counts_df['video_count'] > 0)])}")
    print(f"Mean number of comments per author: {counts_df['comment_count'].mean()}")
    print(f"Mean number of videos per author: {counts_df['video_count'].mean()}")

    interactions_df = video_df.rename(columns={'createtime': 'video_createtime', 'id': 'video_id', 'author': 'video_author', 'desc': 'video_desc', 'hashtags': 'video_hashtags'}) \
        .merge(comment_df.rename(columns={'createtime': 'comment_createtime', 'author': 'comment_author', 'text': 'comment_text'}), on='video_id')

    user_ids = set(counts_df['author'].values)
    video_ids = set(interactions_df['video_id'].values)
    comment_ids = set(interactions_df['comment_id'])

    graph = nx.MultiDiGraph()

    graph_type = 'homogeneous'

    if graph_type == 'homogeneous':
        graph.add_nodes_from(users)

        interactions_df['edge_data'] = interactions_df[['comment_createtime', 'video_hashtags', 'comment_text']].apply(dict, axis=1)
        edges_df = interactions_df[['comment_author', 'video_author', 'edge_data']]
        edges = list(edges_df.itertuples(index=False, name=None))
        graph.add_edges_from(edges)

    elif graph_type == 'heterogeneous':
        graph.add_nodes_from()
        graph.add_edges_from()

    # TODO write to file

if __name__ == '__main__':
    main()