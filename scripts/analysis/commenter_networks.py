from datetime import datetime
import json
import os
import re

import networkx as nx
import pandas as pd
import tqdm

def to_jsonable_dict(row):
    d = {}
    for key, val in row.items():
        if isinstance(val, int) or isinstance(val, str) or isinstance(val, list) or val is None:
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
                    author_name = ''
                    author_id = comment_user['uid']
            else:
                raise Exception()

            comment_text = comment['text']

            mentioned_users = []
            mentions = re.findall('@[^ @]+', comment_text)
            if mentions:
                mentioned_users = [mention[1:] for mention in mentions]

            comments_data.append((
                comment['cid'],
                datetime.fromtimestamp(comment['create_time']), 
                author_name,
                author_id, 
                comment_text,
                mentioned_users,
                comment['aweme_id']
            ))

    comment_df = pd.DataFrame(comments_data, columns=['comment_id', 'createtime', 'author_name', 'author_id', 'text', 'mentions', 'video_id'])
    count_comments_df = comment_df.groupby(['author_id', 'author_name'])[['createtime']].count().reset_index().rename(columns={'createtime': 'comment_count'})

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
    count_vids_df = video_df.groupby(['author_id', 'author_name'])[['createtime']].count().reset_index().rename(columns={'createtime': 'video_count'})

    counts_df = count_vids_df.merge(count_comments_df, how='outer', on=['author_id', 'author_name']).fillna(0)
    counts_df[['video_count', 'comment_count']] = counts_df[['video_count', 'comment_count']].astype(int)

    print(f"Number of users captured: {len(counts_df)}")
    print(f"Number of users who posted a video and no comment: {len(counts_df[(counts_df['comment_count'] == 0) & (counts_df['video_count'] > 0)])}")
    print(f"Number of users who posted a comment and no video: {len(counts_df[(counts_df['comment_count'] > 0) & (counts_df['video_count'] == 0)])}")
    print(f"Number of users who posted a comment and posted a video: {len(counts_df[(counts_df['comment_count'] > 0) & (counts_df['video_count'] > 0)])}")
    print(f"Mean number of comments per author: {counts_df['comment_count'].mean()}")
    print(f"Mean number of videos per author: {counts_df['video_count'].mean()}")

    interactions_df = video_df.rename(columns={'createtime': 'video_createtime', 'author_name': 'video_author_name', 'author_id': 'video_author_id', 'desc': 'video_desc', 'hashtags': 'video_hashtags'}) \
        .merge(comment_df.rename(columns={'createtime': 'comment_createtime', 'author_name': 'comment_author_name', 'author_id': 'comment_author_id', 'text': 'comment_text'}), on='video_id')

    mentions_df = comment_df[['comment_id', 'mentions']].explode('mentions').drop_duplicates().merge(counts_df[['author_id', 'author_name']], how='inner', left_on='mentions', right_on='author_name')

    user_ids = set(counts_df['author_id'].values)
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
        edges_df = interactions_df[['comment_author_id', 'video_author_id', 'edge_data']]
        edges = list(edges_df.itertuples(index=False, name=None))
        graph.add_edges_from(edges)

    elif graph_type == 'heterogeneous':
        graph = nx.Graph()

        counts_df.loc[:, 'type'] = 'user'
        counts_df['author_data'] = counts_df[['author_id', 'author_name', 'comment_count', 'video_count', 'type']].apply(to_jsonable_dict, axis=1)

        video_df.loc[:, 'type'] = 'video'
        video_df['unix_createtime'] = video_df['createtime'].map(pd.Timestamp.timestamp).astype(int)
        video_df['video_data'] = video_df[['video_id', 'unix_createtime', 'author_name', 'desc', 'hashtags', 'type']].apply(to_jsonable_dict, axis=1)

        comment_df.loc[:, 'type'] = 'comment'
        comment_df['unix_createtime'] = comment_df['createtime'].map(pd.Timestamp.timestamp).astype(int)
        comment_df['comment_data'] = comment_df[['comment_id', 'unix_createtime', 'author_name', 'text', 'video_id', 'type']].apply(to_jsonable_dict, axis=1)
        
        nodes_df = pd.concat([
            counts_df[['author_id', 'author_data']].rename(columns={'author_id': 'entity_id', 'author_data': 'node_data'}),
            video_df[['video_id', 'video_data']].rename(columns={'video_id': 'entity_id', 'video_data': 'node_data'}),
            comment_df[['comment_id', 'comment_data']].rename(columns={'comment_id': 'entity_id', 'comment_data': 'node_data'})
        ], ignore_index=True)
        nodes_df = nodes_df.reset_index().rename(columns={'index': 'node_id'})
        all_nodes = list(nodes_df[['node_id', 'node_data']].itertuples(index=False, name=None))
        graph.add_nodes_from(all_nodes)

        video_edges_df = video_df[['author_id', 'video_id']]
        video_edges_df = video_edges_df.merge(nodes_df[['node_id', 'entity_id']], how='left', left_on='author_id', right_on='entity_id').rename(columns={'node_id': 'author_node_id'}) \
                                       .merge(nodes_df[['node_id', 'entity_id']], how='left', left_on='video_id', right_on='entity_id').rename(columns={'node_id': 'video_node_id'})

        user_video_edges = list(video_edges_df[['author_node_id', 'video_node_id']].itertuples(index=False, name=None))
        graph.add_edges_from(user_video_edges)

        user_create_comment_df = comment_df[['author_id', 'comment_id']]
        user_create_comment_df.loc[:, 'type'] = 'create'
        comment_mention_user_df = mentions_df[['comment_id', 'author_id']]
        comment_mention_user_df.loc[:, 'type'] = 'mention'
        user_comment_df = pd.concat([user_create_comment_df, comment_mention_user_df])

        user_comment_df['comment_data'] = user_comment_df[['type']].apply(to_jsonable_dict, axis=1)

        user_comment_df = user_comment_df.merge(nodes_df[['node_id', 'entity_id']], how='left', left_on='author_id', right_on='entity_id').rename(columns={'node_id': 'author_node_id'}) \
                                         .merge(nodes_df[['node_id', 'entity_id']], how='left', left_on='comment_id', right_on='entity_id').rename(columns={'node_id': 'comment_node_id'})

        user_comment_edges = list(user_comment_df[['comment_node_id', 'author_node_id', 'comment_data']].itertuples(index=False, name=None))
        graph.add_edges_from(user_comment_edges)

        interaction_edges_df = interactions_df[['video_id', 'comment_id']]
        interaction_edges_df = interaction_edges_df.merge(nodes_df[['node_id', 'entity_id']], how='left', left_on='video_id', right_on='entity_id').rename(columns={'node_id': 'video_node_id'}) \
                                                   .merge(nodes_df[['node_id', 'entity_id']], how='left', left_on='comment_id', right_on='entity_id').rename(columns={'node_id': 'comment_node_id'})


        comment_video_edges = list(interaction_edges_df[['video_node_id', 'comment_node_id']].itertuples(index=False, name=None))
        graph.add_edges_from(comment_video_edges)

    # write to file
    graph_data = nx.readwrite.node_link_data(graph)

    graph_path = os.path.join(data_dir_path, 'raw_graphs', 'graph_data.json')
    with open(graph_path, 'w') as f:
        json.dump(graph_data, f)

    print("Written new comment graph to file.")

if __name__ == '__main__':
    main()