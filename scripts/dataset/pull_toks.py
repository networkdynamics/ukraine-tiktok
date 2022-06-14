import argparse
import json

from TikTokApi import TikTokApi


def main(args):
    video_data = []

    with TikTokApi() as api:
        for video in api.search.videos('ukraine'):
            video_data.append(video.info_full())

    json.dump(video_data, args.out_path)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--out-path')
    args = parser.parse_args()

    main(args)
