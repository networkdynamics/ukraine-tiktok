import argparse
import json

from TikTokApi import TikTokApi


def main(args):
    video_data = []

    verify_fp = 'verify_l4ej0h1o_LxXoKmAk_T8sx_4sjK_9Naw_Iwn36mubUdc2'

    with TikTokApi(custom_verify_fp=verify_fp) as api:
        for video in api.search.videos('ukraine'):
            video_data.append(video.info_full())

    json.dump(video_data, args.out_path)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--out-path')
    args = parser.parse_args()

    main(args)
