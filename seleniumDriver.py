#!/usr/bin/python

#============================================================================== 
# File:         seleniumDriver.py
# Date:         Fri Mar 10 04:38:52 EST 2017 
# Author(s):    Thalita Coleman <thalitaneu@gmail.com>
# Abstract:     Contains functions that parse twitter html source code and
#               returns page body.
#------------------------------------------------------------------------------ 
#Requirements: Selenium
#============================================================================== 

import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


#----------------------------------------------------
# Name: getSearchBody
# Params: Accepts 1 url and browser
# Abstract: Returns body of search page 
#----------------------------------------------------
def getSearchBody(url, browser):
        browser.get(url)
        browser.execute_script("document.body.style.zoom='50%'")
        time.sleep(1)

        body = browser.find_element_by_tag_name('body')
        bodylen = [1,2,3,4,5]
        i = 0
        while 1 == 1:
		try:
                #body.send_keys(Keys.PAGE_DOWN)
                	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                	sleepamt = float("{0:.2f}".format(random.uniform(0.5,0.8)))
                	time.sleep(sleepamt)
                	body_len = len(body.get_attribute('innerHTML'))
                	i = i + 1
                	bodylen[(i%5)] = body_len
                	if all(x == bodylen[0] for x in bodylen):
                        	break
		except:
			try: 
        			browser.get(url)
        			browser.execute_script("document.body.style.zoom='50%'")
				time.sleep(2)
                		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                		sleepamt = float("{0:.2f}".format(random.uniform(0.5,0.8)))
                		time.sleep(sleepamt)
                		body_len = len(body.get_attribute('innerHTML'))
                		i = i + 1
                		bodylen[(i%5)] = body_len
                		if all(x == bodylen[0] for x in bodylen):
                        		break
			except:
				pass 
			
        body = body.get_attribute('innerHTML')
        return body


#----------------------------------------------------
# Name: getTweetsBody
# Params: Accepts 1 twitter handle and browser
# Abstract: Returns body of tweets and replies page for the specified twitter handle
#----------------------------------------------------
def getTweetsBody(twitterHandle, browser):
        base_url = u'https://twitter.com/'
        end_url = u'/with_replies'
        url = base_url + twitterHandle + end_url

        browser.get(url)
        browser.execute_script("document.body.style.zoom='50%'")
        time.sleep(1)

        body = browser.find_element_by_tag_name('body')
        bodylen = [1,2,3,4,5]
        i = 0
        while 1 == 1:
                #body.send_keys(Keys.PAGE_DOWN)
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleepamt = float("{0:.2f}".format(random.uniform(2.0,3.0)))
                time.sleep(sleepamt)
                body_len = len(body.get_attribute('innerHTML'))
                i = i + 1
                bodylen[(i%5)] = body_len
                if all(x == bodylen[0] for x in bodylen):
                        break
        body = body.get_attribute('innerHTML')
        return body
 
#----------------------------------------------------
# Name: getFollowingBody
# Params: Accepts 1 twitter handle and browser
# Abstract: Log in as user and returns body of 
# following page for the specified twitter handle
#----------------------------------------------------
def getFollowingBody(twitterHandle,browser):

        base_url = u'https://twitter.com/'
        end_url = u'/following'
        url = base_url + twitterHandle + end_url

        browser.get(url)
        browser.execute_script("document.body.style.zoom='50%'")
        time.sleep(1)

        body = browser.find_element_by_tag_name('body')

        bodylen = [1,2,3,4,5]
        i = 0
        while 1 == 1:
                #body.send_keys(Keys.PAGE_DOWN)
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleepamt = float("{0:.2f}".format(random.uniform(0.8,2.6)))
                time.sleep(sleepamt)
                body_len = len(body.get_attribute('innerHTML'))
                i = i + 1
                bodylen[(i%5)] = body_len
                if all(x == bodylen[0] for x in bodylen):
                        break

        body = body.get_attribute('innerHTML')
        return body
 
#----------------------------------------------------
# Name: getFollowersBody
# Params: Accepts 1 twitter handle and browser
# Abstract: Log in as user and returns body of 
# following page for the specified twitter handle
#----------------------------------------------------
def getFollowersBody(twitterHandle,browser):

        base_url = u'https://twitter.com/'
        end_url = u'/followers'
        url = base_url + twitterHandle + end_url

        browser.get(url)
        browser.execute_script("document.body.style.zoom='50%'")
        time.sleep(1)
        body = browser.find_element_by_tag_name('body')

        bodylen = [1,2,3,4,5]
        i = 0
        while 1 == 1:
                #body.send_keys(Keys.PAGE_DOWN)
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleepamt= float("{0:.2f}".format(random.uniform(1.0,2.0)))
                time.sleep(sleepamt)
                body_len = len(body.get_attribute('innerHTML'))
                i = i + 1
                bodylen[(i%5)] = body_len
                if all(x == bodylen[0] for x in bodylen):
                        break

        body = body.get_attribute('innerHTML')
        return body

