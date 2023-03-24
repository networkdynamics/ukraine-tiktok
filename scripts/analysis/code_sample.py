import os

import pandas as pd

from pytok.tiktok import PyTok
from pytok import exceptions

def main():
    sample_type = 'english_and_invasion'

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    video_sample_path = os.path.join(this_dir_path, '..', '..', 'data', 'outputs', f'{sample_type}_video_sample.csv')
    desc_video_sample_path = os.path.join(this_dir_path, '..', '..', 'data', 'outputs', f'desc_{sample_type}_video_sample.csv')

    if os.path.exists(desc_video_sample_path):
        video_sample = pd.read_csv(desc_video_sample_path)
        if 'author_name' not in video_sample.columns:
            video_sample_data = pd.read_csv(video_sample_path)
            video_sample = video_sample.merge(video_sample_data[['video_id', 'author_name']], on='video_id')
    else:
        video_sample = pd.read_csv(video_sample_path)

    # iterate through video ids and view video, wait for coding input
    with PyTok(chrome_version=111) as api:
        for id, video in video_sample.iterrows():
            if not pd.isna(video['my_desc']):
                continue
            try:
                api.video(username=video['author_name'], id=video['video_id']).view()
            except exceptions.NotAvailableException:
                pass
            my_desc = input("Enter a description:")
            video_sample.loc[id, 'my_desc'] = my_desc

    desc_video_sample_path = os.path.join(this_dir_path, '..', '..', 'data', 'outputs', f'desc_{sample_type}_video_sample.csv')
    video_sample[['video_id', 'author_name', 'my_desc']].to_csv(desc_video_sample_path, index=False)


if __name__ == '__main__':
    main()