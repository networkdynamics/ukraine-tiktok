from datetime import datetime
import json
import os
import re

from matplotlib import pyplot as plt
import pandas as pd
import tqdm

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', '..', 'data', 'searches')

    videos = []
    for file_name in os.listdir(data_dir_path):
        file_path = os.path.join(data_dir_path, file_name)
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data

    vids_data = [(video['desc'], datetime.fromtimestamp(video['createTime']), [challenge['title'] for challenge in video.get('challenges', [])]) for video in videos]

    NUM_TOP_HASHTAGS = 100

    video_df = pd.DataFrame(vids_data, columns=['desc', 'createtime', 'hashtags'])
    hashtags_df = video_df.explode('hashtags')

    filter_method = 'top'
    if filter_method == 'top':
        top_hashtags_df = hashtags_df.groupby('hashtags')['desc'].count().sort_values(ascending=False).head(NUM_TOP_HASHTAGS)
        top_hashtags = set(top_hashtags_df.index)

        filtered_hashtags_df = hashtags_df[hashtags_df['hashtags'].isin(top_hashtags)]

    elif filter_method == 'russiavsukraine':
        russiavukraine_words = ['зеленский', 'путинхуйло', 'зеленський', 'путінхуйло']
        russiavukraine = [f"#{word}" for word in russiavukraine_words]
        filtered_hashtags_df = hashtags_df[hashtags_df['hashtags'].isin(russiavukraine)]

    df = filtered_hashtags_df.groupby(['hashtags', pd.Grouper(key='createtime', freq='W')]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 1)

    df = df[df['createtime'] > start_date]
    df = df[df['createtime'] < end_date]

    df = df.pivot_table(index=['createtime'], columns=['hashtags'], fill_value=0).droplevel(0, axis=1)

    df.plot()
    plt.show()


if __name__ == '__main__':
    main()