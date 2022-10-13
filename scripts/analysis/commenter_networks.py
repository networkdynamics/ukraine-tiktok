from datetime import datetime
import json
import os
import re

import networkx as nx
import pandas as pd
import tqdm

import utils

def to_jsonable_dict(row):
    d = {}
    for key, val in row.items():
        if isinstance(val, int) or isinstance(val, str) or val is None:
            json_val = val
        elif isinstance(val, list):
            json_val = ','.join(val)
        else:
            json_val = val
        d[key] = json_val

    return d

def add_edges_to_graph(df, u_id, v_id, edge_columns, graph):
    time_cols = [edge_col for edge_col in edge_columns if 'createtime' in edge_col]
    if len(time_cols) == 1:
        time_col = time_cols[0]
        df['unix_createtime'] = df[time_col].map(pd.Timestamp.timestamp).astype(int)
        edge_columns.remove(time_col)
        edge_columns.append('unix_createtime')
    df['edge_data'] = df[edge_columns].apply(to_jsonable_dict, axis=1)
    edges_df = df[[u_id, v_id, 'edge_data']]
    edges = list(edges_df.itertuples(index=False, name=None))
    graph.add_edges_from(edges)

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    comment_df = utils.get_comment_df()
    video_df = utils.get_video_df()

    sample = 0.02
    if sample:
        comment_df = comment_df.sample(frac=sample)
        video_df = video_df.sample(frac=sample)

    count_comments_df = comment_df[['author_id', 'author_name', 'createtime']].groupby(['author_id', 'author_name']).count().reset_index().rename(columns={'createtime': 'comment_count'})

    video_df = video_df.drop_duplicates('video_id')
    count_vids_df = video_df[['author_id', 'author_name', 'createtime']].groupby(['author_id', 'author_name']).count().reset_index().rename(columns={'createtime': 'video_count'})

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

    mentions_df = comment_df[comment_df['mentions'].str.len() != 0][['author_id', 'mentions', 'text', 'createtime']].explode('mentions').drop_duplicates()
    mentions_df = mentions_df.rename(columns={'mentions': 'mention_id'})

    # add share edges
    shares_df = video_df[video_df['share_video_id'].notna()][['video_id', 'author_id', 'createtime', 'share_video_id', 'share_video_user_id', 'share_type']]

    # add video desc mentions
    video_mentions_df = video_df[video_df['mentions'].str.len() != 0][['video_id', 'author_id', 'createtime', 'mentions']] \
        .explode('mentions').rename(columns={'mentions': 'mention_id'})

    # add comment replies edges
    comment_replies_df = comment_df[comment_df['reply_comment_id'].notna()] \
        .merge(comment_df[comment_df['reply_comment_id'].isna()],
               left_on='reply_comment_id',
               right_on='comment_id',
               suffixes=('_reply', ''),
               how='left') \
        [['comment_id_reply', 'reply_comment_id_reply', 'author_id_reply', 'createtime_reply', 'comment_id', 'author_id']]

    user_ids = set(counts_df['author_id'].values)
    video_ids = set(interactions_df['video_id'].values)
    comment_ids = set(interactions_df['comment_id'].values)
    
    assert user_ids.isdisjoint(video_ids)
    assert video_ids.isdisjoint(comment_ids)
    assert comment_ids.isdisjoint(user_ids)

    graph_type = 'homogeneous'

    if graph_type == 'homogeneous':
        graph = nx.MultiDiGraph()

        graph.add_nodes_from(user_ids)

        # video comment replies
        add_edges_to_graph(interactions_df, 'comment_author_id', 'video_author_id', ['comment_createtime', 'video_hashtags', 'comment_text'], graph)

        # comment mentions
        add_edges_to_graph(mentions_df, 'author_id', 'mention_id', ['createtime', 'text'], graph)

        # video shares
        add_edges_to_graph(shares_df, 'author_id', 'share_video_user_id', ['createtime'], graph)

        # video_desc_mentions
        add_edges_to_graph(video_mentions_df, 'author_id', 'mention_id', ['createtime'], graph)

        # comment replies
        add_edges_to_graph(comment_replies_df, 'author_id_reply', 'author_id', ['createtime_reply'], graph)

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

        #TODO add duet links
        # TODO add comment reply links

    # write to file
    graph_data = nx.readwrite.node_link_data(graph)

    file_name = f'{graph_type}_graph_data.json'
    if sample:
        file_name = str(sample).replace('.', '_') + '_' + file_name

    graph_path = os.path.join(data_dir_path, 'raw_graphs', file_name)
    with open(graph_path, 'w') as f:
        json.dump(graph_data, f)

    print("Written new comment graph to file.")

if __name__ == '__main__':
    main()