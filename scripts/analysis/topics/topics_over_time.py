from datetime import datetime
import json
import os

import matplotlib.pyplot as plt
import pandas as pd

def plot_events(ax, events):
    for event in events:
        ax.axvline(x=event[0])

    for event in events:
        ax.text(event[0], 0.01, event[1], rotation=45)

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..', '..')
    outputs_dir_path = os.path.join(root_dir_path, 'data', 'outputs', '100_clusters')

    topics = [7, 5, 47, 19, 90, 75, 95]
    top_n_topics = 5
    custom_labels = False

    topics_over_time = pd.read_csv(os.path.join(outputs_dir_path, 'topics_over_time.csv'))
    topics_over_time['Timestamp'] = pd.to_datetime(topics_over_time['Timestamp'])

    freq_df = pd.read_csv(os.path.join(outputs_dir_path, 'topic_freqs.csv'))

    with open(os.path.join(outputs_dir_path, 'topic_labels.json'), 'r') as f:
        topic_labels = json.load(f)

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 1)
    topics_over_time = topics_over_time[topics_over_time['Timestamp'] >= start_date]
    topics_over_time = topics_over_time[topics_over_time['Timestamp'] <= end_date]

    freq_df = freq_df.loc[freq_df.Topic != -1, :]
    if topics is not None:
        selected_topics = list(topics)
    elif top_n_topics is not None:
        selected_topics = sorted(freq_df['Topic'].to_list()[:top_n_topics])
    else:
        selected_topics = sorted(freq_df['Topic'].to_list())

    # Prepare data
    topic_names = {int(key): value[value.index('_')+1:].replace('_', ', ')
                    for key, value in topic_labels.items()}
    topics_over_time["Name"] = topics_over_time['Topic'].map(topic_names)
    
    data = topics_over_time.loc[topics_over_time['Topic'].isin(selected_topics), :].sort_values(["Topic", "Timestamp"])

    normalize_frequency = False
    # Add traces
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))
    data = data.set_index('Timestamp')
    data = data.pivot_table(index=['Timestamp'], columns=['Name'], values=['Frequency'], fill_value=0).droplevel(0, axis=1)

    all_count = topics_over_time[['Timestamp', 'Frequency']].groupby('Timestamp').sum()
    data = data.div(all_count['Frequency'], axis=0)

    events = [
        (datetime(2022, 1, 17), 'Russia evacuates its Embassy in Kyiv'),
        (datetime(2022, 2, 23), 'Invasion starts')
    ]
    plot_events(ax, events)

    for column in data.columns:
        ax.plot(data.index, data[column], label=column)

    ax.set_xlabel('Time')
    ax.set_ylabel('Share')
    ax.legend()
    fig.tight_layout()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig.savefig(os.path.join(fig_dir_path, 'topics_over_time.png'))


if __name__ == '__main__':
    main()