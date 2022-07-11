import collections
from gc import collect
import json
import os
import re

import regex
import tqdm
from translate import Translator

meanings = {
    'rusia': "Spanish for Russia",
    'ucraina': "Romanian for Ukraine",
    'xyzbca': "Common TikTok hashtag that means nothing",
    'зсу': "Armed forces of Ukraine",
    'parati': "A kiss for you",
    'путінхуйло': "Ukrainian: Putin sucks",
    'нетвойне': "Russian for No war",
    'путин': "Macedonian for Putin",
    'українапонадусе': "Ukraine above all",
    'ukraina': "Estonian for Ukrainian",
    'perte': "French for loss",
    'fürdich': "German for 'For You'",
    'славаукраїні': "Ukrainian for: 'Glory to Ukraine'",
    'rosja': "Polish for Russia",
    'dlaciebie': "Polish for 'For You'",
    'нівійні': "Ukrainian for 'Non-existent'?",
    'polska': "Polish for Poland",
    'всебудеукраїна': "All of Ukraine",
    'keşfet': "Turkish for Discover",
    'путинхуйло': "Russian: Putin Sucks"
}

def main():

    hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    videos = []
    for hashtag in hashtags:
        print(f"Getting hashtag users: {hashtag}")
        file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data

    descriptions = [video['desc'] for video in videos]

    hashtag_regex = '#\S+'
    all_desc_hashtags = [re.findall(hashtag_regex, desc) for desc in descriptions]
    hashtags = [hashtag for desc_hashtag in all_desc_hashtags for hashtag in desc_hashtag]

    cnt = collections.Counter(hashtags)

    common_hashtags = cnt.most_common(1000)

    russian_translator = Translator(from_lang='uk', to_lang='en')
    ukrainian_translator = Translator(from_lang='ru', to_lang='en')

    translated_hashtags = []
    for hashtag_count in tqdm.tqdm(common_hashtags):
        hashtag, count = hashtag_count
        word = hashtag[1:]
        meaning = ''

        if word in meanings:
            meaning += f"{meanings[word]}"

        elif regex.search(r'\p{IsCyrillic}', word):
            meaning += f", Ukrainian: {ukrainian_translator.translate(word)}"
            meaning += f", Russian: {russian_translator.translate(word)}"

        

        translated_hashtag = (word, meaning, count)
        translated_hashtags.append(translated_hashtag)

    print(translated_hashtags)


if __name__ == '__main__':
    main()