import datetime
import os

import ftlangdetect
import numpy as np
import pandas as pd
import transformers
import tqdm

from pytok import utils

def check_english(text):
    try:
        if text is np.nan:
            return False
        result = ftlangdetect.detect(text)
        return result['lang'] == 'en'
    except Exception as e:
        if str(e) == 'No features in text.':
            return False
        else:
            raise Exception('Unknown error')

def classify_videos(video_df, data_dir_path):
    video_df = video_df[video_df['createtime'].dt.year >= 2022]
    video_df = video_df[video_df['desc'].notna()]

    classifier_dir_path = os.path.join(data_dir_path, 'outputs', 'related_classifier', 'checkpoint-60')
    batch_size = 32

    model = transformers.AutoModelForSequenceClassification.from_pretrained(classifier_dir_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained('roberta-base', model_max_length=512)
    tokenizer_kwargs = {'padding':True,'truncation':True,'max_length':512}
    pipe = transformers.TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True, batch_size=batch_size)
    
    for i in tqdm.tqdm(range(0, len(video_df) + batch_size, batch_size)):
        batch = video_df.iloc[i:min(i+batch_size, len(video_df))]
        outputs = pipe(batch['desc'].tolist(), **tokenizer_kwargs)
        batch.loc[:, 'related_score'] = [pred[1]['score'] for pred in outputs]
        for j, row in batch.iterrows():
            video_df.loc[j, 'related_score'] = row['related_score']

    video_df['related'] = video_df['related_score'] > 0.5
    return video_df

def main():

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    video_path = os.path.join(data_dir_path, 'cache', 'apr_videos.csv')
    video_df = utils.get_video_df(video_path)

    NUM_SAMPLE = 100

    print(f"Total videos: {len(video_df)}")

    sample_type = 'model_half_related'
    if sample_type == 'all':
        video_sample = video_df.sample(NUM_SAMPLE)
    elif sample_type == 'english_and_invasion':
        comment_path = os.path.join(data_dir_path, 'cache', 'all_comments.csv')
        comment_df = utils.get_comment_df(comment_path)
        comment_df['english'] = comment_df['comment_language'] == 'en'
        # get percentage of comments on each video
        video_comments = comment_df[['video_id', 'comment_id', 'english']].groupby('video_id').agg({'english': 'sum', 'comment_id': 'count'})
        video_comments['english_pct'] = video_comments['english'] / video_comments['comment_id']
        
        # join back to videos
        video_df = video_df.merge(video_comments, how='left', left_on='video_id', right_on='video_id')

        # get vids with english descriptions
        video_df['english'] = video_df['desc'].apply(check_english)

        # get vids with at least 50% english comments or english description
        video_df = video_df[(video_df['english_pct'] > 0.5) | (video_df['english'] == True)]
        # get invasion videos
        video_df = video_df[video_df['createtime'].dt.year == 2022]
        video_sample = video_df.sample(NUM_SAMPLE)

    elif sample_type == 'better':
        # filter out videos with description containing high frequency unrelated hashtags
        related_hashtags = ['standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3' \
            'володимирзеленський', 'славаукраїні', 'путінхуйло🔴⚫🇺🇦', 'россия', \
            'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', 'зеленский', 'путинхуйло' \
            'denazification', 'specialmilitaryoperation', 'africansinukraine', 'putinspeech', 'whatshappeninginukraine']
        video_df['related_hashtags'] = video_df['desc'].apply(lambda x: not pd.isna(x) and any([hashtag in x for hashtag in related_hashtags]))
        video_df = video_df[video_df['related_hashtags'] == True]

        comment_path = os.path.join(data_dir_path, 'cache', 'all_comments.csv')
        comment_df = utils.get_comment_df(comment_path)
        comment_df['english'] = comment_df['comment_language'] == 'en'
        # get percentage of comments on each video
        video_comments = comment_df[['video_id', 'comment_id', 'english']].groupby('video_id').agg({'english': 'sum', 'comment_id': 'count'})
        video_comments['english_pct'] = video_comments['english'] / video_comments['comment_id']
        
        # join back to videos
        video_df = video_df.merge(video_comments, how='left', left_on='video_id', right_on='video_id')

        # get vids with english descriptions
        video_df['english'] = video_df['desc'].apply(check_english)

        # get vids with at least 20% english comments or english description
        video_df = video_df[(video_df['english_pct'] > 0.2) | (video_df['english'] == True)]

        # get invasion videos
        video_df = video_df[video_df['createtime'].dt.year == 2022]
        video_sample = video_df.sample(NUM_SAMPLE)

    elif sample_type == 'model':
        video_df = classify_videos(video_df, data_dir_path)
        video_df = video_df[video_df['related'] == True]
        video_sample = video_df.sample(NUM_SAMPLE)

    elif sample_type == 'model_half_related':
        video_df = classify_videos(video_df, data_dir_path)
        video_sample = pd.concat([
            video_df[video_df['related'] == True].sample(NUM_SAMPLE // 2),
            video_df[video_df['related'] == False].sample(NUM_SAMPLE // 2)
        ])  

    print(f"Number filtered videos {len(video_df)}")

    sample_path = os.path.join(data_dir_path, 'outputs', f'{sample_type}_apr_sample.csv')
    video_sample.to_csv(sample_path)

if __name__ == '__main__':
    main()