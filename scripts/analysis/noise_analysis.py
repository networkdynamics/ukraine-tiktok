import pandas as pd

import utils

KEYWORDS = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3', \
    'володимирзеленський', 'славаукраїні', 'путінхуйло', 'россия', 'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', \
    'зеленский', 'путинхуйло', 'denazification', 'specialmilitaryoperation', 'africansinukraine', 'putinspeech', 'whatshappeninginukraine']

def check_keyword_in(desc):
    desc = desc.lower()
    for keyword in KEYWORDS:
        if keyword in desc:
            return True
    else:
        return False

def main():
    video_df = utils.get_video_df()
    video_df['strict_match'] = video_df['desc'].apply(check_keyword_in)

    num_videos = len(video_df)
    num_strict_match = len(video_df[video_df['strict_match']])
    percent_strict_match = 100 * num_strict_match / num_videos

    print(f'Total videos: {num_videos}')
    print(f'Num strict match: {num_strict_match}')
    print(f'Percent strict match: {percent_strict_match}')

    not_strict_match_df = video_df[~video_df['strict_match']]
    not_strict_match_df['desc'].head()

if __name__ == '__main__':
    main()