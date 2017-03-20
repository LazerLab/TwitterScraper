#!/Users/thalitadias/anaconda/bin/python

# -*- coding: utf-8 -*-

##============================================================================== 
# File:		scrapeSourceCode.py		
# Date:		Fri Mar 10 04:46:16 EST 2017
# Author(s):	Thalita Coleman  <thalitaneu@gmail.com>
# Abstract:	Retrieves tweets data from advanced search results.
#		Creates one TSV file for each twitter handle and saves
#		it in the output directory.
#------------------------------------------------------------------------------ 
# Requirements: Python 2.7, BeautifulSoup, Requests, Chromedriver, joblib 
#		function01.py and function02.py
#------------------------------------------------------------------------------ 
# Notes: 	The variable input_file_name is the name of an input file 
#		where each line has a twitter handle.
#============================================================================== 

import os
import requests
from seleniumDriver import *
from getElements2 import *
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
	sourceCode_path = config_d['sourceCode_path'] if 'sourceCode_path' in config_d else 'sourceCode_path/'
	
	with codecs.open(targets_fn) as  fin:
		target_usr_names = fin.readlines()
	
	for root, dirs, files in os.walk(sourceCode_path):
		for f in files:
			target_file = f

logfile = logs_path + "/scrape" + str(datetime.date.today()) + ".log"
log = open(logfile,'w')

privateAcctFile = logs_path + "/privateAccounts" + str(datetime.date.today()) + ".txt"
private = open(privateAcctFile,'w')



def getTweetsFromSourceCode(out_path):
	separator='\t'

# sorts valid urls
	count = 0
	for root, dirs, files in os.walk(sourceCode_path):
        	for f in files:
			#define twitter handle:
			twitterHandle = (str(f)).split('.html',1)[0]
			# creates directory (if not already existed) and file
			if not os.path.exists(out_path):
				os.makedirs(out_path)
			outfile_name_tweets = out_path + '/' + twitterHandle + '.tsv'
			outfile_name_tweets = outfile_name_tweets.replace('\n','')
			of_tweets = open(outfile_name_tweets, "w+")
			of_tweets.write('Type' + separator + 'TimeStamp' + separator + 'Tweet ID' + separator + 'Text' + separator +  'Reference Url' + separator + 'Reference Handle' + separator + 'Language' + separator + '# Replies' + separator + '# Retweets' + separator + '# Likes' + '\n')

			#getting tweets from stored html source
                	filePath = sourceCode_path + '/' + f
                	file = open(filePath, 'r').read()
			file = file.replace('<html', '<neu') 
			file = file.replace('</html', '</neu') 
			file = file.replace('<!DOCTYPE html>', '') 
			file = '<html>' + file + '</html>'
                	#lines = file.readlines()
			count = count + 1
			soup = BeautifulSoup(file, 'html.parser')
			tweetLis= getTweetLis(soup)
			li = tweetLis[0]
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
	return 0


#print getTweetsFromSearchPage(output_path)
results = Parallel(n_jobs=cores, verbose=parallel_verbosity)(delayed(getTweetsFromSourceCode)(output_path) for target in target_file)
