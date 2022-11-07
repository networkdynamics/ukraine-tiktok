import collections
import json
import os

import matplotlib.pyplot as plt
import matplotlib
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
        di_graph = nx.DiGraph()

        filtered_edges = [(u,v) for (u,v,d) in multi_graph.edges(data=True) if edge_filter(d['type'])]
        for u,v in filtered_edges:
            if di_graph.has_edge(u,v):
                di_graph[u][v]['weight'] += 1
            else:
                di_graph.add_edge(u, v, weight=1)

        edge_dir_count = collections.defaultdict(list)
        for u,v,d in di_graph.edges(data=True):
            if (u,v) in edge_dir_count:
                edge_dir_count[(u,v)].append(d['weight'])
            else:
                edge_dir_count[(v,u)].append(d['weight'])

        edge_dir_counts = list(edge_dir_count.values())

        count_shares = [(sum(counts), min(counts) / sum(counts) if len(counts) > 1 else 0) for counts in edge_dir_counts]
        count_share_freq = list(collections.Counter(count_shares).items())
        counts = [c for (c,_),_ in count_share_freq]
        shares = [s for (_,s),_ in count_share_freq]
        freqs = [f for (_,_),f in count_share_freq]

        log_norm = matplotlib.colors.LogNorm()
        scatter = ax.scatter(counts, shares, c=freqs, norm=log_norm)
        plt.colorbar(scatter, ax=ax)
        ax.set_xlabel('Interaction count')
        ax.set_ylabel('Reciprocity')
        ax.set_xscale('log')
        ax.set_title(name)
        ax.set_ylim(bottom=-0.025, top=0.525)

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'edge_dir_share.png'))


if __name__ == '__main__':
    main()