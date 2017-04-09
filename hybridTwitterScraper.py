#!/Users/thalitadias/anaconda/bin/python

# -*- coding: utf-8 -*-

##============================================================================== 
# File:		hybridTwitterScraper.py
# Date:		Mon Mar 20 01:34:34 EDT 2017
# Author(s):	Thalita Coleman  <thalitaneu@gmail.com>
# Abstract:	Retrieves tweets data from advanced search results.
#		Creates one TSV file for each twitter handle and saves
#		it in the output directory.
#------------------------------------------------------------------------------ 
# Requirements: Python 2.7, BeautifulSoup, Requests, Chromedriver, joblib 
#------------------------------------------------------------------------------ 
#============================================================================== 

import os
import requests
from seleniumDriver import *
from getElements import *
from bs4 import BeautifulSoup
from bs4.builder._lxml import LXML
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import timeit
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
	logs_path = config_d['logs_path'] if 'logs_path' in config_d else 'logs/' 
	startDate = config_d['startDate'] if 'startDate' in config_d else '0'
        endDate = config_d['endDate'] if 'endDate' in config_d else '0'
	
	with codecs.open(targets_fn) as  fin:
		target_usr_names = fin.readlines()


separator='\t'

# writing logfile	
if not os.path.exists(logs_path):
        os.makedirs(logs_path)
logfile = logs_path + "/scrape" + str(datetime.date.today()) + ".log"
log = open(logfile,'w')

# writing file to keep private accounts
privateAcctFile = logs_path + "/privateAccounts" + str(datetime.date.today()) + ".txt"
private = open(privateAcctFile,'w')


# writing stats file 
statsFile = sys.argv[0]
statsFile = statsFile.replace('./', '')
statsFile = logs_path + '/' + statsFile.replace('.py', '') + '_' +  datetime.date.today().strftime("%b_%d_%Y") + ".tsv" 
if os.path.exists(statsFile):
	stats = file(statsFile, "r+")
else:
	stats = file(statsFile, "a")
	stats.write('run date' + separator + 'account' + separator + 'join date' + separator + 'tweets/day' + separator + 'total tweets' + separator + 'tweets retrieved' + separator + 'percentage' + separator + 'runtime' + separator +'\n') 


print 'this is the startDate'
print startDate
print type(startDate)
print 'this is the endDate'
print endDate
print type(endDate)


def getTweetsFromSearchPage(target_user, out_path):
	start_time = timeit.default_timer()
	global startDate
        global endDate
	print 'this is the startDate'
	print startDate
	print type(startDate)
	print 'this is the endDate'
	print endDate
	print type(endDate)
# defining twitterHandle
	twitterHandle = target_user.strip()
# launching browser
	browser= webdriver.Chrome('/Users/thalitadias/Downloads/chromedriver')
# getting user's join date
	print 'Processing account: ' + twitterHandle
	feed = getTwitterFeed(twitterHandle)
	soups = BeautifulSoup(feed, 'lxml')
	accountStatus = getAccountStatus(soups)

# testing for private account
	if not  len(accountStatus) == 0:
		private.write(twitterHandle + '\n')
                return 0

# getting user's tweets ammout
        numberTweets = getTweetsAmmount(soups)
        numberTweets = numberTweets.replace(",", "")
	print '# tweets: ' + str(numberTweets)
 
# getting user's Twitter join date
	joinDate = getJoinDate(soups)
	joinDate = str(joinDate)
	if joinDate == 'unknown':
		log.write("Could not find joinDate for " + twitterHandle + '\n')
		return 0
	joinDate = joinDate.split("-", 1)[1]
	joinDate = datetime.datetime.strptime(joinDate, " %d %b %Y")
	print 'the join date is: ' + datetime.datetime.strftime(joinDate, " %d %b %Y")

# defining dates

        if len(startDate) >= 8:
                startDate = startDate.replace("-", " ")
                startDate = datetime.datetime.strptime(startDate, "%d %m %Y")
		startSearch = startDate
        else:
                startSearch = joinDate

        today = dt.datetime.today()

        if len(endDate) >= 8:
                endDate  = endDate.replace("-", " ")
                endDate = datetime.datetime.strptime(endDate, "%d %m %Y")
		endSearch = endDate
        else:
                endSearch = today

	print type(startDate)
	print type(joinDate)
	print type(today)

        if startSearch > joinDate and startSearch < today:
                joinDate = startSearch
        if endSearch > joinDate and endSearch <= today:
                today = endSearch

# setting up range
        totalDays = today - joinDate
        totalDays = str(totalDays).split(" day", 1)
        totalDays = int(totalDays[0])
        tweetsPerDay = int(numberTweets) / totalDays
        tweetsPerDay = round(tweetsPerDay)
	drange = 3
        if tweetsPerDay < 5:
                drange = 5
        print "this is the number of tweets: " + str(numberTweets)
        print "this is the number of days: " + str(totalDays)
        print "this is the range: " + str(drange)

        minus3days = (today + timedelta(days=-drange))
        firstDate = (joinDate + timedelta(days=-drange))

        minus3days = (today + timedelta(days=-3))
        firstDate = (joinDate + timedelta(days=-3))


# generating urls
	urls = []
	while minus3days >=  firstDate:
		url = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A' + twitterHandle+ '%20since%3A' + minus3days.strftime("%Y-%m-%d") + '%20until%3A' + today.strftime("%Y-%m-%d") + '%20include%3Aretweets&src=typd'
		urls.append(url)
		today = minus3days
		minus3days = (today + timedelta(days=-3))


# creating directory (if not already existed) and file
	if not os.path.exists(out_path):
		os.makedirs(out_path)
	outfile_name_tweets = out_path + '/'  + 'w_' + twitterHandle + '.tsv'
	outfile_name_tweets = outfile_name_tweets.replace('\n','')
	of_tweets = open(outfile_name_tweets, "w")
	of_tweets.write('Type' + separator + 'TimeStamp' + separator + 'Tweet ID' + separator + 'Text' + separator +  'Reference Url' + separator + 'Reference Handle' + separator + 'Language' + separator + '# Replies' + separator + '# Retweets' + separator + '# Likes' + '\n')


# sorting and scraping urls
	count = 0
	for url in urls:
		count = count + 1
		if tweetsPerDay > 5:
			pageSource = getSearchBody(url, browser) 
			soup = BeautifulSoup(pageSource, 'lxml')
			emptySearch = soup.find("div", attrs={"SearchEmptyTimeline-empty"})
			if emptySearch is None:
				tweetLis= getTweetLis(soup)
				if not len(tweetLis) > 0:
					log.write("Could not find Lis for " + twitterHandle + '\n')
					return 0  
				li = tweetLis[0]
#writing results to file
				liCount = [] 
				for li in tweetLis:
					liCount.append(1)
                                	of_tweets.write('"' + str(tweetType(li)) + '"'
                                                        + separator + '"' + str(getTimeStamp(li)) + '"'
                                                        + separator + '"' + str(getTweetID(li)) + '"'
                                                        + separator + '"' + str(getTweetText(li)) + '"'
                                                        + separator + '"' + str(getTweetUrl(li)) + '"'
                                                        + separator + '"' + str(getHandle(li)) + '"'
                                                        + separator + '"' + str(getLanguage(li)) + '"'
                                                        + separator + '"' + str(getReplies(li)) + '"'
                                                        + separator + '"' + str(getRetweets(li)) + '"'
                                                        + separator + '"' + str(getLikes(li)) + '"'
                                                        + '\n')

		else:
                        browser.get(url)
                	pageSource = browser.page_source
                        soup = BeautifulSoup(pageSource, 'lxml')
                        emptySearch = soup.find("div", attrs={"SearchEmptyTimeline-empty"})
                        if emptySearch is None:
                                tweetLis= getTweetLis(soup)
                                if not len(tweetLis) > 0:
                                        log.write("Could not find Lis for " + twitterHandle + '\n')
                                        return 0
                                li = tweetLis[0]
#writing results to file
                                liCount = []
                                for li in tweetLis:
                                        liCount.append(1)
                                        of_tweets.write('"' + str(tweetType(li)) + '"'
                                                        + separator + '"' + str(getTimeStamp(li)) + '"'
                                                        + separator + '"' + str(getTweetID(li)) + '"'
                                                        + separator + '"' + str(getTweetText(li)) + '"'
                                                        + separator + '"' + str(getTweetUrl(li)) + '"'
                                                        + separator + '"' + str(getHandle(li)) + '"'
                                                        + separator + '"' + str(getLanguage(li)) + '"'
                                                        + separator + '"' + str(getReplies(li)) + '"'
                                                        + separator + '"' + str(getRetweets(li)) + '"'
                                                        + separator + '"' + str(getLikes(li)) + '"'
                                                        + '\n')

	of_tweets.close()
	#browser.quit()
	runtime = timeit.default_timer() - start_time
	tweetsRetrieved = len(liCount)
	percentage = (float(tweetsRetrieved)/float(numberTweets)) * 100
	percentage = str(percentage) + '%'
	
	#print (datetime.date.today().strftime("%b/%d/%Y") + separator + twitterHandle + separator + datetime.datetime.strftime(joinDate, "%b/%d/%Y") + separator + str(tweetsPerDay) + separator + str(numberTweets) + separator + str(tweetsRetrieved) + separator + percentage + separator + str(runtime) + separator +'\n'
 
	stats.write(datetime.date.today().strftime("%b/%d/%Y") + separator + twitterHandle + separator + datetime.datetime.strftime(joinDate, "%b/%d/%Y") + separator + str(tweetsPerDay) + separator + str(numberTweets) + separator + str(tweetsRetrieved) + separator + percentage + separator + str(runtime) + separator +'\n') 
	stats.close()	
	print 'this is the startDate'
	print startDate
	print type(startDate)
	print 'this is the endDate'
	print endDate
	print type(endDate)
	return 0

results = Parallel(n_jobs=cores, verbose=parallel_verbosity)(delayed(getTweetsFromSearchPage)(target, output_path) for target in target_usr_names)
