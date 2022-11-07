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
        di_graph = nx.DiGraph()

        filtered_edges = [(u,v) for (u,v,d) in multi_graph.edges(data=True) if edge_filter(d['type'])]
        for u,v in filtered_edges:
            if di_graph.has_edge(u,v):
                di_graph[u][v]['weight'] += 1
            else:
                di_graph.add_edge(u, v, weight=1)

        graph = nx.Graph()
        for u,v,d in di_graph.edges(data=True):
            if graph.has_edge(u,v):
                graph[u][v]['dir_counts'].append(d['weight'])
            else:
                graph.add_edge(u, v, dir_counts=[d['weight']])

        recip_j_sim = []
        for u,v,d in graph.edges(data=True):
            u_hashtags = set(multi_graph.nodes[u]['hashtags'])
            v_hashtags = set(multi_graph.nodes[v]['hashtags'])
            j_sim = len(u_hashtags.intersection(v_hashtags)) / len(u_hashtags.union(v_hashtags))
            counts = d['dir_counts']
            recip_share = min(counts) / sum(counts) if len(counts) > 1 else 0
            recip_j_sim.append((recip_share, j_sim))

        recip_j_sim_freq = list(collections.Counter(recip_j_sim).items())
        recip = [r for (r, _),_ in recip_j_sim_freq]
        j_sim = [j_s for (_,j_s),_ in recip_j_sim_freq]
        freqs = [f for (_,_),f in recip_j_sim_freq]

        log_norm = matplotlib.colors.LogNorm()
        scatter = ax.scatter(recip, j_sim, c=freqs, norm=log_norm)
        plt.colorbar(scatter, ax=ax)
        ax.set_xlabel('Reciprocity')
        ax.set_ylabel('Jaccard Similarity')
        ax.set_title(name)
        ax.set_xlim(left=-0.025, right=0.525)
        ax.set_ylim(bottom=-0.05, top=1.05)

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'hashtag_sim_by_reciprocity.png'))


if __name__ == '__main__':
    main()