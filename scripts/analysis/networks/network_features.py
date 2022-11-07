from audioop import mul
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

    graph = nx.Graph(multi_graph)

    degree_freq = nx.degree_histogram(graph)

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.scatter(list(range(len(degree_freq))), degree_freq)
    ax.set_xscale('log')
    ax.set_yscale('log')

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'degree_distribution.png'))

    print(f"Number of connected components: {nx.number_connected_components(graph)}")
    cc_size = [len(c) for c in nx.connected_components(graph)]
    print(f"Largest connected component: {max(cc_size)}")
    print(f"Average connected component size: {sum(cc_size) / len(cc_size)}")
    print(f"Average clustering coefficient: {nx.average_clustering(graph)}")
    print(f"Degree assortivity coefficient: {nx.degree_assortativity_coefficient(graph)}")

if __name__ == '__main__':
    main()