from datetime import datetime
import json
import os

from matplotlib import pyplot as plt
import pandas as pd

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data', 'searches')

    videos = []
    for file_name in os.listdir(data_dir_path):
        file_path = os.path.join(data_dir_path, file_name)
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data

    vids_data = [(datetime.fromtimestamp(video['createTime']), video['author']['uniqueId'], video['desc'], [challenge['title'] for challenge in video.get('challenges', [])]) for video in videos]

    NUM_TOP_HASHTAGS = 100

    video_df = pd.DataFrame(vids_data, columns=['createtime', 'author', 'desc', 'hashtags'])
    
    df = video_df.groupby('author')[['createtime']].count().reset_index().rename(columns={'createtime': 'count'})
    df = df.groupby('count').count().rename(columns={'author': 'num_with_count'})

    df.plot()
    plt.show()


if __name__ == '__main__':
    main()