import os

import pandas as pd

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    cache_dir_path = os.path.join(this_dir_path, '..', '..', 'data', 'cache')

    bot_score_path = os.path.join(cache_dir_path, 'some_users_bot_scores.csv')
    bot_score_df = pd.read_csv(bot_score_path)

    user_df_path = os.path.join(cache_dir_path, 'all_users.csv')
    user_df = pd.read_csv(user_df_path)

    bot_score_df = bot_score_df.merge(user_df, on='uniqueId', how='left')

    # percentage over 0.5
    print(len(bot_score_df[bot_score_df['botness'] > 0.9]) / len(bot_score_df))


if __name__ == '__main__':
    main()