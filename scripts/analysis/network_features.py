import collections
import json
import os

import matplotlib.pyplot as plt
import matplotlib
import networkx as nx

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..')
    data_dir_path = os.path.join(root_dir_path, 'data')

    graph_type = 'homogeneous'
    graph_path = os.path.join(data_dir_path, 'raw_graphs', f'{graph_type}_graph_data.json')
    with open(graph_path, 'r') as f:
        node_link_data = json.load(f)

    multi_graph = nx.node_link_graph(node_link_data)

    # graph = nx.Graph()
    # for u,v in multi_graph.edges():
    #     if graph.has_edge(u,v):
    #         graph[u][v]['weight'] += 1
    #     else:
    #         graph.add_edge(u, v, weight=1)

    # edge_weights = [d['weight'] for u,v,d in graph.edges(data=True)]
    # weight_counts = collections.Counter(edge_weights)
    # weight_counts = sorted(list(weight_counts.items()), key=lambda t: t[0])
    # weights = [weight for weight, count in weight_counts]
    # counts = [count for weight, count in weight_counts]

    # fig, ax = plt.subplots(nrows=1, ncols=1)
    # ax.scatter(weights, counts)
    # ax.set_xscale('log')
    # ax.set_yscale('log')

    # fig.tight_layout()

    # fig_dir_path = os.path.join(root_dir_path, 'figs')
    # fig.savefig(os.path.join(fig_dir_path, 'edge_counts.png'))

    di_graph = nx.DiGraph()
    for u,v in multi_graph.edges():
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

    fig, ax = plt.subplots(nrows=1, ncols=1)

    log_norm = matplotlib.colors.LogNorm()
    ax.scatter(counts, shares, c=freqs, norm=log_norm)
    ax.set_xscale('log')

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'edge_dir_share.png'))

    # degree_freq = nx.degree_histogram(graph)

    # fig, ax = plt.subplots(nrows=1, ncols=1)
    # ax.scatter(list(range(len(degree_freq))), degree_freq)
    # ax.set_xscale('log')
    # ax.set_yscale('log')

    # fig.tight_layout()

    # fig_dir_path = os.path.join(root_dir_path, 'figs')
    # fig.savefig(os.path.join(fig_dir_path, 'degree_distribution.png'))

    # print(f"Number of connected components: {nx.number_connected_components(graph)}")
    # cc_size = [len(c) for c in nx.connected_components(graph)]
    # print(f"Largest connected component: {max(cc_size)}")
    # print(f"Average connected component size: {sum(cc_size) / len(cc_size)}")
    # print(f"Average clustering coefficient: {nx.average_clustering(graph)}")
    # print(f"Degree assortivity coefficient: {nx.degree_assortativity_coefficient(graph)}")

if __name__ == '__main__':
    main()