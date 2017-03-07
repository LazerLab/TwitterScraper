
# File:         README.md
# Date:         Tue Feb 21 13:23:21 EST 2017
# Author(s):    Thalita Coleman  <thalitaneu@gmail.com>
# Abstract:     Describes the process for retrieving tweets data from Twitter.


DESCRIPTION
-----------
This set of scripts parses twitter pages from twitter users listed in a text file (to enter your
file, change the variable input_file_name in twitterScraper.py). It produces tsv files named after
each twitter handle cointaining the following information about each tweet: type (tweet, quote, reply,
retweet, withheld tweet), time stamp, tweet ID, tweet text, reference Url (for retweets and quotes),
reference handle (for retweets and quotes), language, number of replies, number of retweets, number of likes.
The output files are saved in a directory called output there is created inside of the
directory where the program runs.

The program twitterScraper.py retrieves data from twitter advaced search pages. It generates urls
for search inquiries for a particular account  with a three day interval starting from the current day
going all the way back to the day the account was created. It then validate the urls and passes to the scraper
the ones that came out with results. The twitter advanced search does not reliably return retweets, therefore
this scraper returns only tweets, quotes and replies.

REQUIREMENTS:
------------
Python 2.7, BeautifulSoup4, LXML, Requests, Chromedriver, joblib

HOW IT WORKS?
-------------
To execute the set of scripts save your input file with the list of twitter handles in
the directory where you desire to run the scripts. Then open the file twitterScraper.py
and write the name of your input file on the variable input_file_name. Finally, run
twitterScraper.py. * * MAKE SURE YOUR INPUT FILE DOESN'T HAVE EMPTY LINES. * *

The files function01.py, function02.py and your input file should be in the same
directory as twitterScraper.py. twitterScraper.py will make calls to those files.

Here is a diagram that explain what each script does:



 input_file                                                     function01.py & function02.py
 ----------                                                     -----------------------------
Must contain                                            Contains functions that will be called
1 twitter handle                                              by twitterScraper.py to retrieve
per line. Must be \                                              /  various data from twitter.
passed to          \                                            /
twitterScraper.py   \                                          /
                     \                                        /
                                twitterScraper.py
                                -----------------
                   Retrieves tweets data from advanced search
                 results. Creates one TSV file for each twitter
                  handle and saves them in the output directory.
                                        |
                                        |
                                ----------------
                               |     /output    | > Contains tsv files with data for each
                                ________________     twitter handle passed by input file.



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
