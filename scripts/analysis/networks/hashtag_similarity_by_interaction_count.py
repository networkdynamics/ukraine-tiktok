from audioop import mul
import collections
import json
import os

import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import numpy as np
import pandas as pd

def str_to_list(stri):
    if ',' not in stri:
        return []
    return [word.strip()[1:-1] for word in stri[1:-1].split(',')]

def plot_histogram(ax, name, multi_graph, edge_func):
    graph = nx.Graph()
    filtered_edges = [(u,v) for (u,v,d) in multi_graph.edges(data=True) if edge_func]
    for u,v in filtered_edges:
        if graph.has_edge(u,v):
            graph[u][v]['weight'] += 1
        else:
            graph.add_edge(u, v, weight=1)

    weight_j_sim = []
    for u,v in graph.edges():
        u_hashtags = set(multi_graph.nodes[u]['hashtags'])
        v_hashtags = set(multi_graph.nodes[v]['hashtags'])
        j_sim = len(u_hashtags.intersection(v_hashtags)) / len(u_hashtags.union(v_hashtags))
        weight_j_sim.append((graph[u][v]['weight'], j_sim))

    # weight_j_sim_freq = list(collections.Counter(weight_j_sim).items())
    weights = [w for (w, _) in weight_j_sim]
    j_sim = [j_s for (_,j_s) in weight_j_sim]
    # freqs = [f for (_,_),f in weight_j_sim_freq]

    log_norm = matplotlib.colors.LogNorm()
    _, _, _, im = ax.hist2d(weights, j_sim, bins=[10, 10], norm=log_norm)
    plt.colorbar(im, ax=ax)
    ax.set_xlabel('Interaction Count')
    ax.set_ylabel('Jaccard Similarity')
    ax.set_title(name)
    ax.set_ylim(bottom=-0.05, top=1.05)

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..', '..')
    data_dir_path = os.path.join(root_dir_path, 'data')

    graph_type = 'homogeneous'
    graph_path = os.path.join(data_dir_path, 'raw_graphs', f'{graph_type}_graph_data.json')
    with open(graph_path, 'r') as f:
        node_link_data = json.load(f)

    multi_graph = nx.node_link_graph(node_link_data)
    multi_graph.remove_edges_from(nx.selfloop_edges(multi_graph))

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', '..', 'data')
    df_path = os.path.join(data_dir_path, 'cache', 'all_videos.csv')

    videos_df = pd.read_csv(df_path)
    videos_df = videos_df[['author_id', 'hashtags']]
    videos_df['author_id'] = videos_df['author_id'].astype(str)
    videos_df['hashtags'] = videos_df['hashtags'].apply(str_to_list)

    author_hashtags_df = videos_df.explode('hashtags').groupby('author_id').aggregate(list).reset_index()
    author_ids = author_hashtags_df['author_id'].to_list()

    multi_graph = multi_graph.subgraph(author_ids).copy()

    hashtag_attrs = author_hashtags_df.set_index('author_id').to_dict('index')
    nx.set_node_attributes(multi_graph, hashtag_attrs)

    all_types = False

    if all_types:
        edge_filters = {
            'all': lambda edge_type: True,
            'video_comment': lambda edge_type: edge_type == 'video_comment',
            'comment_mention': lambda edge_type: edge_type == 'comment_mention',
            'video_share': lambda edge_type: edge_type == 'video_share',
            'video_mention': lambda edge_type: edge_type == 'video_mention',
            'comment_reply': lambda edge_type: edge_type == 'comment_reply'
        }

        fig, axes = plt.subplots(nrows=1, ncols=len(edge_filters), figsize=(20, 4))

        for ax, (name, edge_filter) in zip(axes, edge_filters.items()):
            edge_func = lambda d: edge_filter(d['type'])
            plot_histogram(ax, name, multi_graph, edge_func)
    else:
        fig = plt.figure()
        ax = fig.add_subplot()
        name = 'All'
        edge_func = lambda d: True
        plot_histogram(ax, name, multi_graph, edge_func)

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'hashtag_sim_by_edge_count.png'))


if __name__ == '__main__':
    main()