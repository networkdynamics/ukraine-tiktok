import os

import pandas as pd

def main():
    sample_type = 'all'
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    desc_video_sample_path = os.path.join(this_dir_path, '..', '..', 'data', 'outputs', f'desc_{sample_type}_video_sample.csv')

    desc_video_sample = pd.read_csv(desc_video_sample_path)

    num_total = len(desc_video_sample)
    percent_related = desc_video_sample['related'].str.contains('Y').sum() / num_total
    percent_unrelated = desc_video_sample['related'].str.contains('N').sum() / num_total
    percent_unavailable = desc_video_sample['related'].isna().sum() / num_total

    print(f"Percent related: {percent_related}, percent unrelated: {percent_unrelated}, percent unavailable: {percent_unavailable}")
    print(f"Of available, percent related: {desc_video_sample['related'].str.contains('Y').sum() / desc_video_sample['related'].notna().sum()}, percent unrelated: {desc_video_sample['related'].str.contains('N').sum() / desc_video_sample['related'].notna().sum()}")

if __name__ == '__main__':
    main()