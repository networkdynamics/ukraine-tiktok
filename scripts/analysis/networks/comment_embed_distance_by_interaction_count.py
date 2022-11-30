import collections
import json
import os

import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import numpy as np
import pandas as pd

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..', '..')
    data_dir_path = os.path.join(root_dir_path, 'data')

    graph_type = 'homogeneous'
    graph_path = os.path.join(data_dir_path, 'raw_graphs', f'{graph_type}_graph_data.json')
    with open(graph_path, 'r') as f:
        node_link_data = json.load(f)

    multi_graph = nx.node_link_graph(node_link_data)

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', '..', 'data')
    df_path = os.path.join(data_dir_path, 'cache', 'all_english_comments.csv')

    comments_df = pd.read_csv(df_path)
    comments_df = comments_df[['author_id']]
    comments_df['author_id'] = comments_df['author_id'].astype(str)

    embeddings_cache_path = os.path.join(data_dir_path, 'cache', 'all_english_comment_twitter_roberta_embeddings.npy')
    with open(embeddings_cache_path, 'rb') as f:
        embeddings = np.load(f)

    comments_df['embeddings'] = list(embeddings)
    comment_users_df = comments_df.groupby('author_id').aggregate(np.mean).reset_index()
    author_ids = comment_users_df['author_id'].to_list()

    multi_graph = multi_graph.subgraph(author_ids).copy()

    comment_attrs = comment_users_df.set_index('author_id').to_dict('index')
    nx.set_node_attributes(multi_graph, comment_attrs)

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

        fig, axes = plt.subplots(nrows=1, ncols=len(edge_filters), figsize=(20,4))

        for ax, (name, edge_filter) in zip(axes, edge_filters.items()):
            graph = nx.Graph()
            filtered_edges = [(u,v) for (u,v,d) in multi_graph.edges(data=True) if edge_filter(d['type'])]
            for u,v in filtered_edges:
                if graph.has_edge(u,v):
                    graph[u][v]['weight'] += 1
                else:
                    graph.add_edge(u, v, weight=1)

            weight_cos_sim = []
            for u,v in graph.edges():
                u_embedding = multi_graph.nodes[u]['embeddings']
                v_embedding = multi_graph.nodes[v]['embeddings']
                cos_sim = np.dot(u_embedding, v_embedding) / (np.linalg.norm(u_embedding) * np.linalg.norm(v_embedding))
                weight_cos_sim.append((graph[u][v]['weight'], cos_sim))

            weight_cos_sim_freq = list(collections.Counter(weight_cos_sim).items())
            weights = [w for (w, _),_ in weight_cos_sim_freq]
            cos_sim = [c_s for (_,c_s),_ in weight_cos_sim_freq]
            freqs = [f for (_,_),f in weight_cos_sim_freq]

            log_norm = matplotlib.colors.LogNorm()
            scatter = ax.scatter(weights, cos_sim, c=freqs, norm=log_norm)
            plt.colorbar(scatter, ax=ax)
            ax.set_xlabel('Interaction Count')
            ax.set_ylabel('Cosine Similarity')
            ax.set_xscale('log')
            ax.set_title(name)
            ax.set_ylim(bottom=-0.05, top=1.05)
    else:
        fig = plt.figure()
        ax = fig.add_subplot()

        graph = nx.Graph()
        filtered_edges = [(u,v) for (u,v,d) in multi_graph.edges(data=True)]
        for u,v in filtered_edges:
            if graph.has_edge(u,v):
                graph[u][v]['weight'] += 1
            else:
                graph.add_edge(u, v, weight=1)

        weight_cos_sim = []
        for u,v in graph.edges():
            u_embedding = multi_graph.nodes[u]['embeddings']
            v_embedding = multi_graph.nodes[v]['embeddings']
            cos_sim = np.dot(u_embedding, v_embedding) / (np.linalg.norm(u_embedding) * np.linalg.norm(v_embedding))
            weight_cos_sim.append((graph[u][v]['weight'], cos_sim))

        weight_cos_sim_freq = list(collections.Counter(weight_cos_sim).items())
        weights = [w for (w, _),_ in weight_cos_sim_freq]
        cos_sim = [c_s for (_,c_s),_ in weight_cos_sim_freq]
        freqs = [f for (_,_),f in weight_cos_sim_freq]

        log_norm = matplotlib.colors.LogNorm()
        scatter = ax.scatter(weights, cos_sim, c=freqs, norm=log_norm, s=1)
        plt.colorbar(scatter, ax=ax)
        ax.set_xlabel('Interaction Count')
        ax.set_ylabel('Cosine Similarity')
        ax.set_xscale('log')
        ax.set_ylim(bottom=-0.05, top=1.05)

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'comment_sim_by_edge_counts.png'))


if __name__ == '__main__':
    main()