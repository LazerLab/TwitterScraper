
File:         README.md
Date:         Fri Mar 10 04:38:52 EST 2017
Author(s):    Thalita Coleman  <thalitaneu@gmail.com>
Abstract:     Describes the process for retrieving tweets data from Twitter.


DESCRIPTION
-----------
This set of scripts scrapes tweets from Twitter advanced search page. Before using this script, 
you should collect tweets available on the API (to collect tweets from twitter API 
we suggest using this library: https://github.com/kennyjoseph/twitter_dm.git). This scripts will collect 
the tweets that could not be collect from the API because of the rate limit.
It produces tsv files named after each twitter handle cointaining the following information about each tweet: 
type (tweet, quote, reply, retweet, withheld tweet), time stamp, tweet ID, tweet text, reference Url (for retweets and quotes),
reference handle (for retweets and quotes), language, number of replies, number of retweets, number of likes.
The output files are saved in a directory called output there is created inside of the
directory where the program runs.

REQUIREMENTS:
------------
Python 2.7, BeautifulSoup4, LXML, Requests, Chromedriver, joblib

USAGE
------

After inslalling all the required packages and libraries and properly editing the 
config file, run twitterScraper.py scraper.config


TSV FILES:
---------
The CSV files contain the following header:
Type, TimeStamp, Tweet ID, Text, Reference Url, Reference Handle, Language, # Replies, # Retweets, # Likes
All fields are delimited by double quotes and separated by tabs.

META CHARACTERS:
---------------
Here are some characters that were substituted to preserve formatting:

 " - Double quotation marks were replaced by <quote>.

\n - New lines were repleced by <newline>.
