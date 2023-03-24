import botometer

def main():
    rapidapi_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    blt = botometer.BotometerLite(rapidapi_key=rapidapi_key)

    # Prepare a list of tweets from the users that you want to perform bot detection on.
    # The list should contain no more than 100 tweets.
    tweet_list = [tweet1, tweet2, ...] 

    blt_scores = blt.check_accounts_from_tweets(tweet_list)

if __name__ == '__main__':
    main()