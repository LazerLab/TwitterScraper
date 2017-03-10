##============================================================================== 
# File:         validateTwitterScraper.py
# Date:         Fri Mar 10 04:46:16 EST 2017
# Author(s):    Thalita Coleman  <thalitaneu@gmail.com>
# Abstract:     Retrieves tweets data from advanced search results.
#               Creates one TSV file for each twitter handle and saves
#               it in the output directory.
#------------------------------------------------------------------------------ 
# Requirements: Python 2.7, BeautifulSoup, Requests, Chromedriver, joblib 
#               function01.py and function02.py
#------------------------------------------------------------------------------ 
# Notes:        The variable input_file_name is the name of an input file 
#               where each line has a twitter handle.
#============================================================================== 

from pyvirtualdisplay import Display
import os
import requests
from seleniumDriver import *
from getElements import *
from bs4 import BeautifulSoup
from bs4.builder._lxml import LXML
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import datetime as dt
from datetime import timedelta
import random
import re
import codecs
import sys
from joblib import Parallel, delayed
reload(sys)
sys.setdefaultencoding('utf8')


def load_dict_file(fn, verbose = False):
    """assumes each line contains at least 2 tab/space separated elements. 
        Further elements (e.g. comments) will be ignored. 
    """
    with open(fn) as fin:
        d = {}
        for l in fin:
            a = l.strip().split()
            d[a[0]]=a[1]
    if verbose:
        print d

    return d





if __name__ == "__main__":

        #reading config file and setting default params
        config_fn = sys.argv[1]
        config_d = load_dict_file(config_fn, True)
        #TODO log config_d 
        targets_fn = config_d['targets_fn']
        #TODO err and exit if config_d['targets_fn'] key error.

        output_path = config_d['output_path'] if 'output_path' in config_d else 'output/'
        cores = int(config_d['cores']) if 'cores' in config_d else 4
        parallel_verbosity = int(config_d['parallel_verbosity']) if 'parallel_verbosity' in config_d else 5
        general_verbosity = config_d['general_verbosity'] if 'general_verbosity' in config_d else False
        logs_path = config_d['logs_path'] if 'logs_path' in config_d else output_path

        with codecs.open(targets_fn) as  fin:
                target_usr_names = fin.readlines()
                
                
logfile = logs_path + "/scrape" + str(datetime.date.today()) + ".log"
log = open(logfile,'w')

privateAcctFile = logs_path + "/privateAccounts" + str(datetime.date.today()) + ".txt"
private = open(privateAcctFile,'w')

def getTweetsFromSearchPage(target_user, out_path):
        separator='\t'
# define twitterHandle
        twitterHandle = target_user.strip()
        #twitterHandle = #twitterHandle.replace('\n', '')
# launch browser
        display = Display(visible=0, size=(1600,1200))
        display.start()
        browser= webdriver.Chrome('/home/tcoleman/chromedriver')
# get user's join date
        print 'Processing account: ' + twitterHandle
        feed = getTwitterFeed(twitterHandle)
        soups = BeautifulSoup(feed, 'html.parser')
        accountStatus = getAccountStatus(soups)
        print 'defining account status'
        if not  len(accountStatus) == 0:
                private.write(twitterHandle + '\n')
                return 0
        joinDate = getJoinDate(soups)
        joinDate = str(joinDate)
        print 'defining joinDate'
        if joinDate == 'unknown':
                log.write("Could not find joinDate for " + twitterHandle + '\n')
                return 0
        joinDate = joinDate.split("-", 1)[1]
        joinDate = datetime.datetime.strptime(joinDate, " %d %b %Y")

# define dates
        today = dt.datetime.today()
        minus3days = (today + timedelta(days=-3))
        firstDate = (joinDate + timedelta(days=-3))

# generate urls
        urls = []
        while minus3days >=  firstDate:
                url = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A' + twitterHandle+ '%20since%3A' + minus3days.strftime("%Y-%m-%d") + '%20until%3A' + today.strftime("%Y-%m-%d") + '%20include%3Aretweets&src=typd'
                urls.append(url)
                today = minus3days
                minus3days = (today + timedelta(days=-3))
        print 'Generated ' + str(len(urls)) + ' urls for '+ twitterHandle


# creates directory (if not already existed) and file
        print 'Creating file: ' + 'validate' + twitterHandle + '.tsv'
        if not os.path.exists(out_path):
                os.makedirs(out_path)
        outfile_name_tweets = out_path + '/' + 'validate' + twitterHandle + '.tsv'
        outfile_name_tweets = outfile_name_tweets.replace('\n','')
        of_tweets = open(outfile_name_tweets, "w")
        of_tweets.write('Type' + separator + 'TimeStamp' + separator + 'Tweet ID' + separator + 'Text' + separator +  'Reference Url' + separator + 'Reference Handle' + separator + 'Language' + separator + '# Replies' + separator + '# Retweets' + separator + '# Likes' + '\n')

# sorts valid urls
        count = 0
        for url in urls:
                count = count + 1
                browser.get(url)
                pageSource = browser.page_source
                soup = BeautifulSoup(pageSource, 'html.parser')
                emptySearch = soup.find("div", attrs={"SearchEmptyTimeline-empty"})
                if emptySearch is None:
                        tweetLis= getTweetLis(soup)
                        if not len(tweetLis) > 0:
                                log.write("Could not find Lis for " + twitterHandle + '\n')
                                return 0
                        li = tweetLis[0]
                        print 'Processing url ' + str(count) + ' out of ' + str(len(urls)) + ' for '+ twitterHandle + '. Url: ' + url
                        for li in tweetLis:
                                print 'Writing results to file'
                                of_tweets.write('"' + tweetType(li) + '"'
                                                        + separator + '"' + getTimeStamp(li) + '"'
                                                        + separator + '"' + getTweetID(li) + '"'
                                                        + separator + '"' + getTweetText(li) + '"'
                                                        + separator + '"' + getTweetUrl(li) + '"'
                                                        + separator + '"' + getHandle(li) + '"'
                                                        + separator + '"' + getLanguage(li) + '"'
                                                        + separator + '"' + getReplies(li) + '"'
                                                        + separator + '"' + getRetweets(li) + '"'
                                                        + separator + '"' + getLikes(li) + '"'
                                                        + '\n')
        of_tweets.close()
        browser.quit()
        return 0

results = Parallel(n_jobs=cores, verbose=parallel_verbosity)(delayed(getTweetsFromSearchPage)(target, output_path) for target in target_usr_names)
