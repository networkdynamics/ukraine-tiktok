import os

import transformers
import tqdm

from pytok import utils

def main():

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    file_name = 'apr_videos.csv'
    video_path = os.path.join(data_dir_path, 'cache', file_name)
    video_df = utils.get_video_df(video_path)

    print(f"Total videos: {len(video_df)}")

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
    video_df = video_df[video_df['related'] == True]

    print(f"Number filtered videos {len(video_df)}")

    sample_path = os.path.join(data_dir_path, 'outputs', 'related_apr_videos.csv')
    video_df.to_csv(sample_path)
    
if __name__ == '__main__':
    main()