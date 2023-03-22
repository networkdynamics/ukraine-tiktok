import os

import pandas as pd

from pytok.tiktok import PyTok

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    video_sample_path = os.path.join(this_dir_path, '..', '..', 'data', 'outputs', 'video_sample.csv')

    video_sample = pd.read_csv(video_sample_path)

    # iterate through video ids and view video, wait for coding input
    with PyTok() as api:
        for id, video in video_sample.iterrows():
            api.video(id=video['video_id']).view()


if __name__ == '__main__':
    main()