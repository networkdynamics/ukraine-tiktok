# Invasion of Ukraine on TikTok Dataset

## Description

This is a dataset of videos and comments related to the invasion of Ukraine, published on TikTok by a number of users over the year of 2022. It was compiled by Benjamin Steel, Sara Parker and Derek Ruths at the Network Dynamics Lab, McGill University. We created this dataset to facilitate the study of TikTok, and the nature of social interaction on the platform relevant to a major political event. For more details, see the paper on this dataset [https://arxiv.org/abs/2301.08305](https://arxiv.org/abs/2301.08305)

The dataset has been released on Zenodo: [https://doi.org/10.5281/zenodo.7926959](https://doi.org/10.5281/zenodo.7926959) as well as on Github: [https://github.com/networkdynamics/ukraine-tiktok](https://github.com/networkdynamics/ukraine-tiktok)

To create the dataset, we identified hashtags and keywords explicitly related to the conflict to collect a core set of videos (or ”TikToks”). We then filtered the dataset to a more related to the invasion set of videos. We then compiled comments associated with these videos. All of the data captured is publically available information, and contains personally identifiable information. In total we collected approximately 9.5 thousand videos. From a subset of these videos, we scraped 4.4 million comments from 2.6 million users, but scraping more comments is possible. The author personally collected this data using the web scraping PyTok library, developed by the author: [https://github.com/networkdynamics/pytok](https://github.com/networkdynamics/pytok). 

We release here the unique video IDs of the dataset in a CSV format. The data was collected without the specific consent of the content creators, so we have released only the data required to re-create it, to allow users to delete content from TikTok and be removed from the dataset if they wish. Contained in this repository are scripts that will automatically pull the full dataset, which will take the form of JSON files organised into a folder for each video. The JSON files are the entirety of the data returned by the TikTok API. We include a script to parse the JSON files into CSV files with the most commonly used data. We plan to further expand this dataset as collection processes progress and the war continues. We will version the dataset to ensure reproducibility.

We have also released some additional data here: The raw video IDs from the initial collection, pre-filtering. And we also release the coded dataset used to train the filtering model, to improve the transparency of that process, and what we consider related to the invasion.

## Building

To build this dataset from the IDs here:

1. Go to [https://github.com/networkdynamics/pytok](https://github.com/networkdynamics/pytok) and clone the repo locally
2. Run `pip install -e .` in the pytok directory
3. Run `pip install pandas tqdm` to install these libraries if not already installed
4. Run `get_videos.py` to get the video data
5. Run `video_comments.py` to get the comment data
6. Run `user_tiktoks.py` to get the video history of the users
7. Run `hashtag_tiktoks.py` or `search_tiktoks.py` to get more videos from other hashtags and search terms
8. Run `load_json_to_csv.py` to compile the JSON files into two CSV files, `comments.csv` and `videos.csv`

If you get an error about the wrong chrome version, use the command line argument `get_videos.py --chrome-version YOUR_CHROME_VERSION`
Please note pulling data from TikTok takes a while! We recommend leaving the scripts running on a server for a while for them to finish downloading everything. Feel free to play around with the delay constants to either speed up the process or avoid TikTok rate limiting.

You might also consider using the faster, original David Teather TikTokApi library [https://github/davidteather/tiktok-api](https://github.com/davidteather/tiktok-api) when it is working!

Please do not hesitate to make an issue in this repo to get our help with this!

## Contents

The `videos.csv` will contain the following columns:
|Field name | Description |
|----------|----------|
|`video_id`| Unique video ID |
|`createtime`| UTC datetime of video creation time in YYYY-MM-DD HH:MM:SS format |
|`author_name`| Unique author name |
|`author_id`| Unique author ID |
|`desc`| The full video description from the author |
|`hashtags`| A list of hashtags used in the video description |
|`share_video_id`| If the video is sharing another video, this is the video ID of that original video, else empty |
|`share_video_user_id`| If the video is sharing another video, this the user ID of the author of that video, else empty |
|`share_video_user_name`| If the video is sharing another video, this is the user name of the author of that video, else empty |
|`share_type`| If the video is sharing another video, this is the type of the share, stitch, duet etc. |
|`mentions`| A list of users mentioned in the video description, if any |
|`digg_count`| The number of likes on the video |
|`share_count`| The number of times the video was shared |
|`comment_count`| The number of comments on the video |
|`play_count`| The number of times the video was played |

The `comments.csv` will contain the following columns:
|Field name | Description |
|----------|-----------|
|`comment_id`| Unique comment ID |
|`createtime`| UTC datetime of comment creation time in YYYY-MM-DD HH:MM:SS format |
|`author_name`| Unique author name |
|`author_id`| Unique author ID |
|`text`| Text of the comment |
|`mentions`| A list of users that are tagged in the comment |
|`video_id`| The ID of the video the comment is on |
|`comment_language`| The language of the comment, as predicted by the TikTok API |
|`digg_count`| The number of likes the comment got |
|`reply_comment_id`| If the comment is replying to another comment, this is the ID of that comment |

The `users.csv` will contain the following columns:
|Field name | Description |
|----------|-----------|
|`id`| Unique author ID |
|`uniqueId`| Unique user name |
|`nickname`| Display user name, changeable |
|`signature`| Short user description |
|`verified`| Whether or not the user is verified |
|`followingCount`| How many other accounts the user is following |
|`followerCount`| How many followers the user has |
|`videoCount`| How many videos the user has made |
|`diggCount`| How many total likes the user has had |
|`createtime`| When the user account was made. This is derived from the `id` field, and can occasionally be incorrect with a very low unix epoch such as 1971 |

The date can be compiled into a user interaction network to facilitate study of interaction dynamics. There is code to help with that here: [https://github.com/networkdynamics/polar-seeds](https://github.com/networkdynamics/polar-seeds). Additional scripts for further preprocessing of this data can be found there too.

## Cite

If you use this dataset, please cite the paper [https://arxiv.org/abs/2301.08305](https://arxiv.org/abs/2301.08305)!

## Ethical Statement

The data was collected without the specific consent of the content creators, so we have released only the data required to re-create it, to allow users to delete content from TikTok and be removed from the dataset if they wish.

