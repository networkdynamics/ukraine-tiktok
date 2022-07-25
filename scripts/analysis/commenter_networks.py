from datetime import datetime
import json
import os

import networkx as nx
import pandas as pd
import tqdm

def to_jsonable_dict(row):
    d = {}
    for key, val in row.items():
        if isinstance(val, int) or isinstance(val, str) or isinstance(val, list):
            json_val = val
        else:
            json_val = val
        d[key] = json_val

    return d

def main():
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
            comment_user = comment['user']
            if isinstance(comment_user, str):
                continue
            elif isinstance(comment_user, dict):
                if 'unique_id' in comment_user:
                    author_id = comment_user['uid']
                    author_name = comment_user['unique_id']
                elif 'uniqueId' in comment_user:
                    author_id = comment_user['id']
                    author_name = comment_user['uniqueId']
                else:
                    author_name = None
                    author_id = comment_user['uid']
            else:
                raise Exception()

            comments_data.append((
                comment['cid'],
                datetime.fromtimestamp(comment['create_time']), 
                author_name,
                author_id, 
                comment['text'],
                comment['aweme_id']
            ))

    comment_df = pd.DataFrame(comments_data, columns=['comment_id', 'createtime', 'author_name', 'author_id', 'text', 'video_id'])
    count_comments_df = comment_df.groupby('author_id')[['createtime']].count().reset_index().rename(columns={'createtime': 'comment_count'})

    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
               + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

    vids_data = []
    for file_path in tqdm.tqdm(file_paths):
        with open(file_path, 'r') as f:
            videos = json.load(f)

        vids_data += [
            (
                video['id'],
                datetime.fromtimestamp(video['createTime']), 
                video['author']['uniqueId'], 
                video['author']['id'],
                video['desc'], 
                [challenge['title'] for challenge in video.get('challenges', [])]
            ) 
            for video in videos
        ]

    video_df = pd.DataFrame(vids_data, columns=['video_id', 'createtime', 'author_name', 'author_id', 'desc', 'hashtags'])
    video_df = video_df.drop_duplicates('video_id')
    count_vids_df = video_df.groupby('author_id')[['createtime']].count().reset_index().rename(columns={'createtime': 'video_count'})

    counts_df = count_vids_df.merge(count_comments_df, how='outer', on='author_id').fillna(0)
    counts_df[['video_count', 'comment_count']] = counts_df[['video_count', 'comment_count']].astype(int)

    print(f"Number of users captured: {len(counts_df)}")
    print(f"Number of users who posted a video and no comment: {len(counts_df[(counts_df['comment_count'] == 0) & (counts_df['video_count'] > 0)])}")
    print(f"Number of users who posted a comment and no video: {len(counts_df[(counts_df['comment_count'] > 0) & (counts_df['video_count'] == 0)])}")
    print(f"Number of users who posted a comment and posted a video: {len(counts_df[(counts_df['comment_count'] > 0) & (counts_df['video_count'] > 0)])}")
    print(f"Mean number of comments per author: {counts_df['comment_count'].mean()}")
    print(f"Mean number of videos per author: {counts_df['video_count'].mean()}")

    interactions_df = video_df.rename(columns={'createtime': 'video_createtime', 'author_name': 'video_author_name', 'author_id': 'video_author_id', 'desc': 'video_desc', 'hashtags': 'video_hashtags'}) \
        .merge(comment_df.rename(columns={'createtime': 'comment_createtime', 'author': 'comment_author', 'text': 'comment_text'}), on='video_id')

    user_ids = set(counts_df['author'].values)
    video_ids = set(interactions_df['video_id'].values)
    comment_ids = set(interactions_df['comment_id'].values)
    
    assert user_ids.isdisjoint(video_ids)
    assert video_ids.isdisjoint(comment_ids)
    assert comment_ids.isdisjoint(user_ids)

    graph_type = 'heterogeneous'

    if graph_type == 'homogeneous':
        graph = nx.MultiDiGraph()

        graph.add_nodes_from(user_ids)

        interactions_df['edge_data'] = interactions_df[['comment_createtime', 'video_hashtags', 'comment_text']].apply(dict, axis=1)
        edges_df = interactions_df[['comment_author', 'video_author', 'edge_data']]
        edges = list(edges_df.itertuples(index=False, name=None))
        graph.add_edges_from(edges)

    elif graph_type == 'heterogeneous':
        graph = nx.Graph()

        counts_df['author_data'] = counts_df[['comment_count', 'video_count']].apply(to_jsonable_dict, axis=1)
        author_nodes = list(counts_df[['author', 'author_data']].itertuples(index=False, name=None))
        graph.add_nodes_from(author_nodes)

        video_df['unix_createtime'] = video_df['createtime'].map(pd.Timestamp.timestamp).astype(int)
        video_df['video_data'] = video_df[['unix_createtime', 'author', 'desc', 'hashtags']].apply(to_jsonable_dict, axis=1)
        video_nodes = list(video_df[['video_id', 'video_data']].itertuples(index=False, name=None))
        graph.add_nodes_from(video_nodes)

        comment_df['unix_createtime'] = comment_df['createtime'].map(pd.Timestamp.timestamp).astype(int)
        comment_df['comment_data'] = comment_df[['unix_createtime', 'author', 'text', 'video_id']].apply(to_jsonable_dict, axis=1)
        comment_nodes = list(comment_df[['comment_id', 'comment_data']].itertuples(index=False, name=None))
        graph.add_nodes_from(comment_nodes)

        user_video_edges = list(video_df[['author', 'video_id']].itertuples(index=False, name=None))
        graph.add_edges_from(user_video_edges)

        user_comment_edges = list(comment_df[['author', 'comment_id']].itertuples(index=False, name=None))
        graph.add_edges_from(user_comment_edges)

        comment_video_edges = list(interactions_df[['video_id', 'comment_id']].itertuples(index=False, name=None))
        graph.add_edges_from(comment_video_edges)

    # write to file
    graph_data = nx.readwrite.node_link_data(graph)

    graph_path = os.path.join(data_dir_path, 'raw_graph', 'graph_data.json')
    with open(graph_path, 'w') as f:
        json.dump(graph_data, f)

    print("Written new comment graph to file.")

if __name__ == '__main__':
    main()