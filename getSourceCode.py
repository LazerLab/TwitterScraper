#!/Users/thalitadias/anaconda/bin/python
# -*- coding: utf-8 -*-

##============================================================================== 
# File:		getSourceCode.py
# Date:		Fri Mar 10 04:17:03 EST 2017
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
	sourceCode_path = config_d['sourceCode_path'] if 'sourceCode_path' in config_d else 'sourceCode_path/'
	
	with codecs.open(targets_fn) as  fin:
		target_usr_names = fin.readlines()

# writing logfile	
logfile = logs_path + "/scrape" + str(datetime.date.today()) + ".log"
log = open(logfile,'w')

# writing file to keep private accounts
privateAcctFile = logs_path + "/privateAccounts" + str(datetime.date.today()) + ".txt"
private = open(privateAcctFile,'w')



def getSourceCode(target_user, sourceCode_path):
	separator='\t'
# define twitterHandle
	twitterHandle = target_user.strip()
	#twitterHandle = #twitterHandle.replace('\n', '')
# launch browser
	browser= webdriver.Chrome('/Users/thalitadias/Downloads/chromedriver')
# get user's join date
	print 'Processing account: ' + twitterHandle
	feed = getTwitterFeed(twitterHandle)
	soups = BeautifulSoup(feed, 'html.parser')
	accountStatus = getAccountStatus(soups)
# testing for private account
	if not  len(accountStatus) == 0:
		private.write(twitterHandle + '\n')
                return 0
# getting user's join date
	joinDate = getJoinDate(soups)
	joinDate = str(joinDate)
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

# retrive source-code
	for url in urls:
		browser.get(url)
		pageSource = browser.page_source


# creates directory (if not already existed) and file
	print 'Creating source-code file: ' + twitterHandle + '.html'
	if not os.path.exists(sourceCode_path):
		os.makedirs(sourceCode_path)
	source_code = sourceCode_path + '/' + twitterHandle + '.html'
	source_code = source_code.replace('\n','')
	of_source_code = open(source_code, "w")

# retrive source-code
        for url in urls:
                browser.get(url)
                pageSource = browser.page_source
		of_source_code.write(pageSource)


	of_source_code.close()
	browser.quit()
	return 0

results = Parallel(n_jobs=cores, verbose=parallel_verbosity)(delayed(getSourceCode)(target, sourceCode_path) for target in target_usr_names)
