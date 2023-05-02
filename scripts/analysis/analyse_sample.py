import os

import pandas as pd

def main():
    sample_name = 'desc_model_half_related_apr_video_sample.csv'

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    video_sample_path = os.path.join(this_dir_path, '..', '..', 'data', 'outputs', sample_name)

    df = pd.read_csv(video_sample_path)

    # num true positive
    pred_related = df.iloc[:50]
    print(f"True positive: {pred_related[pred_related['my_related'] == 'Y']['my_desc'].count() / 50}")
    print(f"False positive: {pred_related[pred_related['my_related'] == 'N']['my_desc'].count() / 50}")
    pred_unrelated = df.iloc[50:]
    print(f"True negative: {pred_unrelated[pred_unrelated['my_related'] == 'N']['my_desc'].count() / 50}")
    print(f"False negative: {pred_unrelated[pred_unrelated['my_related'] == 'Y']['my_desc'].count() / 50}")

if __name__ == '__main__':
    main()