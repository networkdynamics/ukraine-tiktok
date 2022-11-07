import collections
import json
import os
import re

import regex
import tqdm

meanings = {
    'володимирзеленський': "Ukrainian for 'Volodymr Zelensky'",
    'славаукраїні': "Ukrainian for: 'Glory to Ukraine'",
    'путінхуйло': "Ukrainian for 'Putin sucks'",
    'рек': "Ukrainian for 'Recommended'",
    'україна': "Ukrainian for 'Ukraine'",
    'рекомендации': "Ukrainian for 'Recommendations'",
    'рекомендації': "Ukrainian for 'Recommendations'",
    'россия': "Ukrainian for 'Russia'",
    'украина': "Ukrainian for 'Ukraine'",
    'Україна': "ukrainian for 'Ukraine'",
    'війнавукраїні': "Ukrainian for 'War in Ukraine'",
    'зеленський': "Ukrainian for 'Zelensky'",
    'хочуврек': "Ukrainian for 'I want recommends'?",
    'нівійні': "Ukrainian for 'Non-existent'?",
    'війна': "Ukrainian for 'War'",
    'війна2022': "Ukrainian for 'War2022'",
    'українськийтікток': "Ukrainian for 'Ukrainian TikTok'",
    'президент': "Ukrainian for 'President'",
    'війнатриває': "Ukrainian for 'The War Continues'",
    'українапереможе': "Ukrainian for 'Ukraine will win'",
    'київ': "Ukrainian for 'Kyiv'",
    'макрон': "Ukrainian for 'Macron'",
    'порошенко': "Ukrainian for 'Poroshenko', ex-Prime Minister of Ukraine",
    'европа': "Ukrainian for 'Europe'",

    'нетвойне': "Russian for 'No war'",
    'тренды': "Russian for 'Trends'",
    'зеленский': "Russian for 'Zelensky'",
    'путинхуйло': "Russian for 'Putin Sucks'",
    'героямслава': "Russian for 'Glory to the Heroes'",
    'юмор': "Russian for 'Funny'",
    'политика': "Russian for 'Politics'",
    'мир': "Russian for 'World' or 'Peace'",
    'переписка': "Russian for 'Correspondence'",
    'Россия': "Russian for 'Russia'",
    'зе': "Russian for 'Ze', Short name for Zelensky?",
    'сша': "Russian for 'USA'",
    'владимирзеленский': "Russian for 'Vladimir Zelensky'",
    'НАТО': "Russian for 'NATO'",
    'донбасс': "Russian for 'Donbass'",

    'rusia': "Spanish for 'Russia'",
    'parati': "Spanish for 'For You'",
    'ucrania': "Spanish for 'Ukraine'",
    'guerra': "Spanish for 'War'",

    'ucraina': "Romanian for 'Ukraine'",
    
    'путин': "Macedonian for 'Putin'",
    'москва': "Macedonian for 'Moscow'",

    'українапонадусе': "Ukraine above all",
    'ukraina': "Estonian for 'Ukrainian'",
    'perte': "French for 'loss'",
    'fürdich': "German for 'For You'",
    
    'rosja': "Polish for 'Russia'",
    'dlaciebie': "Polish for 'For You'",
    'polska': "Polish for 'Poland'",

    'всебудеукраїна': "All of Ukraine",
    'keşfet': "Turkish for 'Discover'",
    
    'война': "Bulgarian for 'War'",

    'xyzbca': "Common TikTok hashtag that means nothing",
    'зсу': "Armed forces of Ukraine",
    'CapCut': "Video Editor",
}

def main():

    #hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    #hashtags = ['володимирзеленський', 'славаукраїні', 'путінхуйло🔴⚫🇺🇦', 'россия', 
    #'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', 'зеленский', 'путинхуйло']
    #hashtags = ['denazification', 'specialmilitaryoperation', 'africansinukraine', 'putinspeech', 'whatshappeninginukraine']

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
    
    hashtag_dir_path = os.path.join(data_dir_path, 'hashtags')
    searches_dir_path = os.path.join(data_dir_path, 'searches')
    file_paths = [os.path.join(hashtag_dir_path, file_name) for file_name in os.listdir(hashtag_dir_path)] \
               + [os.path.join(searches_dir_path, file_name) for file_name in os.listdir(searches_dir_path)]

    videos = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data

    all_desc_hashtags = [[challenge['title'] for challenge in video.get('challenges', [])] for video in videos]
    hashtags = [hashtag for desc_hashtag in all_desc_hashtags for hashtag in desc_hashtag]

    cnt = collections.Counter(hashtags)

    common_hashtags = cnt.most_common(1000)

    #russian_translator = Translator(from_lang='uk', to_lang='en')
    #ukrainian_translator = Translator(from_lang='ru', to_lang='en')

    translated_hashtags = []
    for hashtag_count in tqdm.tqdm(common_hashtags):
        hashtag, count = hashtag_count
        word = hashtag
        meaning = ''

        if word in meanings:
            meaning += f"{meanings[word]}"

        #elif regex.search(r'\p{IsCyrillic}', word):
            #meaning += f", Ukrainian: {ukrainian_translator.translate(word)}"
            #meaning += f", Russian: {russian_translator.translate(word)}"

        translated_hashtags.append({
            'word': word,
            'meaning': meaning,
            'count': count
        })

    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(this_file_dir, '..', '..', 'data', 'outputs')
    hashtag_file = os.path.join(data_dir, 'all_common_hashtags.json')

    with open(hashtag_file, 'w') as f:
        json.dump(translated_hashtags, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()