import os

from pytok import utils

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))

    videos_dir_path = os.path.join(this_dir_path, 'data', 'videos')

    video_data_paths = []
    comment_data_paths = []
    for dir_name in os.listdir(videos_dir_path):
        video_data_path = os.path.join(videos_dir_path, dir_name, 'video_data.json')
        if os.path.exists(video_data_path):
            video_data_paths.append(video_data_path)

        comment_data_path = os.path.join(videos_dir_path, dir_name, 'video_comments.json')
        if os.path.exists(comment_data_path):
            comment_data_paths.append(comment_data_path)

    cache_dir_path = os.path.join(this_dir_path, 'data', 'cache')

    if not os.path.exists(cache_dir_path):
        os.mkdir(cache_dir_path)

    comment_cache_path = os.path.join(cache_dir_path, 'comments.csv')
    video_cache_path = os.path.join(cache_dir_path, 'videos.csv')
    user_cache_path = os.path.join(cache_dir_path, 'users.csv')

    comment_df = utils.get_comment_df(comment_cache_path, file_paths=comment_data_paths)
    video_df = utils.get_video_df(video_cache_path, file_paths=video_data_paths)
    user_df = utils.get_user_df(user_cache_path, file_paths=video_data_paths + comment_data_paths)

    # Do some analysis!

if __name__ == '__main__':
    main()