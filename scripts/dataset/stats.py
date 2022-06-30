import json
import os

from TikTokApi import TikTokApi

def main():
    hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3']
    
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    for hashtag in hashtags:
        print("-" * 10)
        print(f"Hashtag: #{hashtag}")

        file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        print(f"Number of videos: {len(video_data)}")

        users = list(set([video['author']['uniqueId'] for video in video_data]))
        print(f"Number of unique users: {len(users)}")

if __name__ == '__main__':
    main()