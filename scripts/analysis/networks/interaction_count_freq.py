import collections
import json
import os

import matplotlib.pyplot as plt
import networkx as nx

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

        fig, axes = plt.subplots(nrows=1, ncols=len(edge_filters), sharey=True, figsize=(20, 4))

        for ax, (name, edge_filter) in zip(axes, edge_filters.items()):
            graph = nx.Graph()
            filtered_edges = [(u,v) for (u,v,d) in multi_graph.edges(data=True) if edge_filter(d['type'])]
            for u,v in filtered_edges:
                if graph.has_edge(u,v):
                    graph[u][v]['weight'] += 1
                else:
                    graph.add_edge(u, v, weight=1)

            edge_weights = [d['weight'] for u,v,d in graph.edges(data=True)]
            weight_counts = collections.Counter(edge_weights)
            weight_counts = sorted(list(weight_counts.items()), key=lambda t: t[0])
            weights = [weight for weight, count in weight_counts]
            counts = [count for weight, count in weight_counts]

            scatter = ax.scatter(weights, counts)
            ax.set_xlabel('Interaction Count')
            ax.set_ylabel('Frequency')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_title(name)
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

        edge_weights = [d['weight'] for u,v,d in graph.edges(data=True)]
        weight_counts = collections.Counter(edge_weights)
        weight_counts = sorted(list(weight_counts.items()), key=lambda t: t[0])
        weights = [weight for weight, count in weight_counts]
        counts = [count for weight, count in weight_counts]

        scatter = ax.scatter(weights, counts)
        ax.set_xlabel('Interaction Count')
        ax.set_ylabel('Frequency')
        ax.set_xscale('log')
        ax.set_yscale('log')

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'edge_counts.png'))


if __name__ == '__main__':
    main()