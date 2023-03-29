import os

import pandas as pd

from pytok import utils

import video_sample

def main():
    sample_type = 'all'
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    video_sample_path = os.path.join(data_dir_path, 'outputs', f'{sample_type}_video_sample.csv')
    video_sample = pd.read_csv(video_sample_path, parse_dates=['createtime'])

    desc_video_sample_path = os.path.join(data_dir_path, 'outputs', f'desc_{sample_type}_video_sample.csv')
    desc_video_sample = pd.read_csv(desc_video_sample_path)

    desc_video_sample = video_sample.merge(desc_video_sample, on='video_id')

    comment_path = os.path.join(data_dir_path, 'cache', 'all_comments.csv')
    comment_df = utils.get_comment_df(comment_path)
    comment_df['english'] = comment_df['comment_language'] == 'en'
    # get percentage of comments on each video
    video_comments = comment_df[['video_id', 'comment_id', 'english']].groupby('video_id').agg({'english': 'sum', 'comment_id': 'count'})
    video_comments['english_pct'] = video_comments['english'] / video_comments['comment_id']
    
    # join back to videos
    video_sample = unrelated_sample.merge(video_comments, how='left', left_on='video_id', right_on='video_id')

    # get vids with english descriptions
    video_sample['english'] = video_sample['desc'].apply(video_sample.check_english)

    num_total = len(desc_video_sample)
    num_related = desc_video_sample['related'].str.contains('Y').sum()
    num_unrelated = desc_video_sample['related'].str.contains('N').sum()
    num_unavailable = desc_video_sample['related'].isna().sum()
    num_available = num_total - num_unavailable
    percent_related = num_related / num_total
    percent_unrelated = num_unrelated / num_total
    percent_unavailable = num_unavailable / num_total

    print(f"Percent related: {percent_related}, percent unrelated: {percent_unrelated}, percent unavailable: {percent_unavailable}")
    print(f"Of available, percent related: {num_related / num_available}, percent unrelated: {num_unrelated / num_available}")

    # analysis of related videos
    related_sample = desc_video_sample[(desc_video_sample['related'].notna()) & (desc_video_sample['related'].str.contains('Y'))]
    related_years = related_sample['createtime'].dt.year.value_counts()
    print(f"Related video years: {related_years.to_dict()}")

    percent_english_description = related_sample['english'].sum() / len(related_sample)
    percent_english_comments = related_sample['english_pct'].mean()
    print(f"Percent english description: {percent_english_description}, percent english comments: {percent_english_comments}")

    # analysis of unrelated videos
    unrelated_sample = desc_video_sample[(desc_video_sample['related'].notna()) & (desc_video_sample['related'].str.contains('N'))]
    unrelated_years = unrelated_sample['createtime'].dt.year.value_counts()
    print(f"Unrelated video years: {unrelated_years.to_dict()}")

    percent_english_description = unrelated_sample['english'].sum() / len(unrelated_sample)
    percent_english_comments = unrelated_sample['english_pct'].mean()
    print(f"Percent english description: {percent_english_description}, percent english comments: {percent_english_comments}")

if __name__ == '__main__':
    main()