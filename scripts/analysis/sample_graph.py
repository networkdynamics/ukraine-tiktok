import json
import os
import random

import matplotlib.pyplot as plt
import networkx as nx

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..')
    data_dir_path = os.path.join(root_dir_path, 'data')

    graph_type = 'homogeneous'
    graph_path = os.path.join(data_dir_path, 'raw_graphs', f'{graph_type}_graph_data.json')
    with open(graph_path, 'r') as f:
        node_link_data = json.load(f)

    graph = nx.node_link_graph(node_link_data)

    graph = nx.Graph(graph)

    k = 10
    N = 2
    core_nodes = set(random.sample(graph.nodes, k))
    for _ in range(N):
        core_nodes.update(set(neighbour for node in core_nodes for neighbour in graph[node]))

    sampled_graph = graph.subgraph(core_nodes)

    for n, d in sampled_graph.nodes(data=True):
        d.clear()

    for u, v, d in sampled_graph.edges(data=True):
        d.clear()

    nx.readwrite.write_gexf(sampled_graph, os.path.join(data_dir_path, 'raw_graphs', f'sample_{k}_{N}_homogeneous_graph_data.gexf'))

if __name__ == '__main__':
    main()