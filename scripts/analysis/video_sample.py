import os

import pandas as pd

import utils

def main():

    video_df = utils.get_video_df()
    video_df = video_df.drop_duplicates('video_id')

    NUM_SAMPLE = 100
    video_sample = video_df.sample(NUM_SAMPLE)

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    sample_path = os.path.join(data_dir_path, 'outputs', 'video_sample.csv')
    video_sample.to_csv(sample_path)

if __name__ == '__main__':
    main()