from datetime import datetime
import collections
import json
import os
import re

from matplotlib import pyplot as plt
import pandas as pd
import tqdm

def main():

    file_hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    videos = []
    for hashtag in file_hashtags:
        print(f"Getting hashtag users: {hashtag}")
        file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data

    hashtag_regex = '#\S+'
    vids_data = [(video['desc'], datetime.fromtimestamp(video['createTime']), re.findall(hashtag_regex, video['desc'])) for video in videos]

    video_df = pd.DataFrame(vids_data, columns=['desc', 'createtime', 'hashtags'])
    hashtags_df = video_df.explode('hashtags')

    top_hashtags_df = hashtags_df.groupby('hashtags')['desc'].count().sort_values(ascending=False).head(100)
    top_hashtags = set(top_hashtags_df.index)

    df = hashtags_df[hashtags_df['hashtags'].isin(top_hashtags)].groupby(['hashtags', pd.Grouper(key='createtime', freq='W')]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    df = df.pivot_table(index=['createtime'], columns=['hashtags'], fill_value=0)

    df.plot()
    plt.show()


if __name__ == '__main__':
    main()