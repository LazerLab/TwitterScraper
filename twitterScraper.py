#!/home/tcoleman/venv/twitter/bin/python

# -*- coding: utf-8 -*-
##============================================================================== 
# file:			twitterscraper.py
# date:			Tue Sep 26 10:37:11 EDT 2017
# author(s):		Thalita Coleman  <thalitaneu@gmail.com>
# abstract:		retrieves tweets data from advanced search results using
#			dynamic search ranges.
#			creates one tsv file for each twitter handle and saves
#			it in the output directory.
#------------------------------------------------------------------------------ 
# requirements: python 2.7, beautifulsoup, requests, chromedriver, joblib 
#------------------------------------------------------------------------------ 
##============================================================================== 

import requests
import re
import codecs
import sys
import os
import subprocess 
from subprocess import call

from bs4 import BeautifulSoup
from bs4.builder._lxml import LXML
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

import time
import timeit
from datetime import timedelta
import datetime as dt
import datetime
import random

from joblib import Parallel, delayed
import simplejson as json
import json

from jsonParser import *
from seleniumDriver import *
from getElements import *

reload(sys)
sys.setdefaultencoding('utf8')


# enable/disable debug messages
debug= False
debug2= False

# global storage for tweetli's
alltweetlis= []


def load_dict_file(fn, verbose = False): 
    """assumes each line contains at least 2 tab/space separated elements. 
        further elements (e.g. comments) will be ignored. 
    """
    with open(fn) as fin:
        d = {}
        for l in fin:
            a = l.strip().split()
            d[a[0]]=a[1]
    if verbose:
        print d, '\n\n' 
        
    return d
   

if __name__ == "__main__":
		
	#reading config file and setting default params
	config_fn = sys.argv[1]
	config_d = load_dict_file(config_fn, True)
	
	output_path = config_d['output_path'] if 'output_path' in config_d else 'output/' 
	cores = int(config_d['cores']) if 'cores' in config_d else 4
	parallel_verbosity = int(config_d['parallel_verbosity']) if 'parallel_verbosity' in config_d else 5
	general_verbosity = config_d['general_verbosity'] if 'general_verbosity' in config_d else False
	logs_path = config_d['logs_path'] if 'logs_path' in config_d else 'logs/' 
	startDate = config_d['startDate'] if 'startDate' in config_d else '0'
	endDate = config_d['endDate'] if 'endDate' in config_d else '0'
	json_path = config_d['json_path']
	jsonParsed_path = config_d['jsonParsed_path']

	# reading files on json_path
	for root, dirs, files in os.walk(json_path):
		target_usrs = files


# writing logfile	
if not os.path.exists(logs_path):
       	os.makedirs(logs_path)
logFile = logs_path + "/stats_" + datetime.date.today().strftime("%b_%d_%Y") + ".log"


def getTweetsFromApi(target_user, out_path):
	global logs
	global jsonParsed_path

# defining twitterHandle
	#twitterHandle = target_user.split('.json', 1)		#use if the json files are .json
	twitterHandle = target_user.split('.json.gz', 1)	#use if the json files are .json.gz
	twitterHandle = twitterHandle[0]
	target_usr_json = json_path + '/' + target_user
	
	if not os.path.exists(out_path):
		os.makedirs(out_path)
	outfile_name_tweets = out_path + '/'  +  datetime.date.today().strftime("%b_%d_%y") + '_' + twitterHandle + '.tsv'
	outfile_name_tweets = outfile_name_tweets.replace('\n','')
	
	try:
		global linesJson
		linesJson = subprocess.check_output(['wc', '-l', target_usr_json]) 
		linesJson = linesJson.split(' /', 1)
		linesJson = int(linesJson[0])
		
# parses json file and write data to TSV	
		if linesJson > 0:
			tweetCount, joinDate, lastApiTweet, statuses_count = jsonToCsv(target_usr_json, outfile_name_tweets)

# moves parsed json file to jsonParsed directory
			if not os.path.exists(jsonParsed_path):
				os.makedirs(jsonParsed_path)
			call(["mv", target_usr_json, jsonParsed_path])

# counts number of tweets retrieved via API and decides calls the 
# getTweetsFromSearchPage function if not all tweets were retrieved already
			if tweetCount < statuses_count:
				getTweetsFromSearchPage(twitterHandle, joinDate, lastApiTweet, outfile_name_tweets, tweetCount)  
			else:
				print twitterHandle, ': all tweets were retrieved from API', '\n\n'
		else:
			print "empty file"
	except OSError:
		    print "No file"

# retrieves tweets from the advanced search page
def getTweetsFromSearchPage(twitterHandle, joinDate, startDate, outFile, tweetCount):
	separator='\t'

# launchs browser
	display = Display(visible=0, size=(1600,1200))
    	display.start()
    	browser= webdriver.Chrome('/home/tcoleman/chromedriver') # give the location of Chrome
	#browser= webdriver.Chrome('/Users/ellery/thalitabin/chromedriver')

# gets total number of tweets for account
	feed = getTwitterFeed(twitterHandle)
	soups = BeautifulSoup(feed, 'lxml')
	#accountStatus = getAccountStatus(soups)
	global numberTweets
	numberTweets = getTweetsAmmount(soups)
	numberTweets = numberTweets.replace(',','')
	numberTweets = numberTweets.replace('.','')
	print twitterHandle, '>>> total number of tweets for this account is:', str(numberTweets), 'Retrieving tweets from search page.', '\n\n'

# initializes global var allTweetLi's to [] for each twitterHandle
	global allTweetLis
	allTweetLis= []

# definines dates
	joinDate = re.match('(.*?)(\w+\s\d+\s)(\d+\:\d+\:\d+\s\+\d+\s)(\d+)', joinDate)
	joinDate = joinDate.group(2) + joinDate.group(4)
	elJoinDate = datetime.datetime.strptime(joinDate, "%b %d %Y")

	startDate = re.match('(.*?)(\w+\s\d+\s)(\d+\:\d+\:\d+\s\+\d+\s)(\d+)', startDate)
	startDate = startDate.group(2) + startDate.group(4)
	elToday = datetime.datetime.strptime(startDate, "%b %d %Y")


# calculates the number of days between today and the users's join date
	elDelta= elToday - elJoinDate
	elDays= elDelta.days

	#print "\n\n\nThe number of days between ", elJoinDate, " and ", elToday, ": ", elDays

# counts how many tweets were returned by the rearch. 
# If =< 1 tweets were returned, the time range will be doubled for the next search
	threeDayRanges= [];
	i=1
	d=2
	minTweets = 1
	while(i < elDays):
		range='{0}-{1}'.format(i,i+d)
		#print 'i: ' + str(i)
		#print 'd: ' + str(d)
		if( testRange(browser,twitterHandle,elJoinDate,range,minTweets) == True ):
			i = i+d
			d = 2
			#print 'range for TRUE: ' + str(range)
			#print 'new i: ' + str(i)
			#print 'new d: ' + str(d)
		else:
			i = i+d
			d = d * 2
			#print 'range for FALSE: ' + str(range)
			#print 'new i: ' + str(i)
			#print 'new d: ' + str(d)
			#print '\n\n\----------------------'
	#print "\nthreeDayRanges: " + str(threeDayRanges)
	#print "\nnumber of 3-day ranges: ", len(threeDayRanges)

	original3DayRangeCount= len(threeDayRanges)


# prints all the results to a TSV file
	writeResults(twitterHandle,outFile,separator,numberTweets, joinDate, tweetCount)
	browser.quit()	# stop browser
    	display.stop()	# stop display



#----------------------------------------------------
# testRange: counts how many tweets were returned
# in a given search range
#----------------------------------------------------
def testRange(browser,twitterHandle,joinDate,range,minTweets):
	global allTweetLis

	#retrieve integer range
	thirtyDayBegin= int(range.split('-')[0])
	thirtyDayEnd= int(range.split('-')[1])

	#convert range integers to actual dates
	thirtyDayBegin= joinDate + timedelta(days=thirtyDayBegin)
	thirtyDayEnd= joinDate + timedelta(days=thirtyDayEnd)

	# debugging messages
	if(debug):
		print "\n"
		print "debug: thirtyDayBegin: ", thirtyDayBegin
		print "debug: thirtyDayEnd: ", thirtyDayEnd

	# Searchs this range on twitter.  If the result set is greater than
	# or equal to minTweets, return True.  Otherwise, return False.
	searchResults= twitterSearch(browser,twitterHandle,thirtyDayBegin,thirtyDayEnd)
	#print "searchResultsLen: ", len(searchResults)

	if len(searchResults) >= minTweets:
		allTweetLis.append(searchResults)
		return True
	else:
		return False



#----------------------------------------------------
# twitterSearch: searchs for a give range and returns twwets Lis
#----------------------------------------------------
def twitterSearch(browser,twitterHandle,beginDate,endDate):
	tweetLis= []
	urls= []
	url = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A' + twitterHandle+ '%20since%3A' + beginDate.strftime("%Y-%m-%d") + '%20until%3A' + endDate.strftime("%Y-%m-%d") + '%20include%3Aretweets&src=typd'
	urls.append(url)


# sorts and scrapes urls
	for url in urls:
		pageSource = getSearchBody(url, browser) 
		soup = BeautifulSoup(pageSource, 'lxml')
		emptySearch = soup.find("div", attrs={"SearchEmptyTimeline-empty"})
		if emptySearch is None:
			tweetLis= getTweetLis(soup)
		if not len(tweetLis) > 0:
			pass
			#print "Could not find Lis for ", twitterHandle, '\n'
	return tweetLis




#----------------------------------------------------
# writeResults: writes results to TSV file 
#----------------------------------------------------
def writeResults(twitterHandle,outFile,separator, numberTweets, joinDate, tweetCount):
	global allTweetLis
	of_tweets = open(outFile, "a")

	#writing results to file
	#print 'writing results to file'
	for liList in allTweetLis:
		for li in liList:
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

	# writing log file
	
	tweetsRetrieved = int(len(allTweetLis)) + int(tweetCount) 
	numberTweets = int(numberTweets)
	percentage = (float(tweetsRetrieved)/float(numberTweets)) * 100
        percentage = float("{0:.2f}".format(percentage))
        percentage = str(percentage) + '%'
	
	if os.path.exists(logFile):	
		logs = open(logFile, "a")
	else:
		logs = open(logFile, "a")
        	logs.write('run_date' + separator + 'account' + separator + 'join_date' + separator + 'total_tweets' + separator + 'retrieved_from_api' + separator + 'retrieved_from_searchPage' + separator + 'total_retrieved' + separator + 'percentage_retrieved' + separator +'\n')

	logs.write(datetime.date.today().strftime("%b/%d/%Y") + separator + twitterHandle + separator + joinDate + separator + str(numberTweets) + separator + str(tweetCount) + separator + str(len(allTweetLis)) + separator + str(tweetsRetrieved) + separator + percentage + separator + '\n')
	
# starts script using joblib. Check config file to modify paths and number 
# of cores used 
results = Parallel(n_jobs=cores, verbose=parallel_verbosity)(delayed(getTweetsFromApi)(target, output_path) for target in target_usrs)

