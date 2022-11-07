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
        graph = nx.Graph()
        filtered_edges = [(u,v,d) for (u,v,d) in multi_graph.edges(data=True) if edge_filter(d['type'])]

        ms_per_day = 10 * 60 * 60 * 24

        edge_times = collections.defaultdict(list)
        for u,v,d in filtered_edges:
            if (u,v) in edge_times:
                edge_times[(u,v)].append(d['unix_createtime'] / ms_per_day)
            else:
                edge_times[(v,u)].append(d['unix_createtime'] / ms_per_day)

        sorted_times = [sorted(times) for times in edge_times.values() if len(times) > 1]
        avg_time_intervals = [(times[-1] - times[0]) / len(times) for times in sorted_times]
        time_intervals = [times[-1] - times[0] for times in sorted_times]

        ax.hist(time_intervals, bins=100, label='Average Interaction Time')
        ax.hist(avg_time_intervals, bins=100, label='Average Interaction Interval')
        ax.legend()
        ax.set_yscale('log')
        ax.set_xlabel('Days')
        ax.set_ylabel('Frequency')
        ax.set_title(name)

    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'interaction_time_intervals.png'))


if __name__ == '__main__':
    main()