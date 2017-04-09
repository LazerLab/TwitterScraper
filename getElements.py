#!/usr/bin/python

#============================================================================== 
# File:         getElements.py         
# Date:         Fri Mar 10 04:38:52 EST 2017
# Author(s):    Thalita Coleman <thalitaneu@gmail.com>
# Abstract:     Contains functions to retrieve data from twitter. 
#------------------------------------------------------------------------------ 
# Requirements: BeautifulSoup, Selenium, Requests, datetime  
#==============================================================================

import requests
import re
from seleniumDriver import *
from bs4 import BeautifulSoup
from bs4.builder._lxml import LXML
import datetime
import datetime as dt
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


#----------------------------------------------------
# Name: getTwitterFeed
# Params: Accepts 1 twitter handle
# Abstract: Returns content of the page
#----------------------------------------------------
def getTwitterFeed(twitterHandle):
        base_url = u'https://twitter.com/'
        end_url = u'/with_replies'
        url = base_url + twitterHandle + end_url
        r = requests.get(url)
        return r.text


#----------------------------------------------------
# Name: getAccountStatus
# Params: Accepts soup for 1 twitter handle
# Abstract: Returns account status: private or public
#----------------------------------------------------
def getAccountStatus(soups):
	accountStatus = soups.findAll('div', {'class': "ProtectedTimeline"})
	return accountStatus


#----------------------------------------------------
# Name: getJoinDate
# Params: Accepts soup for 1 twitter handle
# Abstract: Returns date the user joined twitter
#----------------------------------------------------
def getJoinDate(soup):
	joindate=''
        spans= soup.findAll('span')
        for s in spans:
                if s.has_attr('class'):
                        if 'ProfileHeaderCard-joinDateText' in s['class']:
                                sDict = s.attrs #this is a dictionary
                                joindate = sDict.get('title') #gets the value for title
	if joindate == '':
		joindate= 'unknown'
	return joindate


#----------------------------------------------------
# Name: getTweetsAmmount
# Params: Accepts soup for 1 twitter handle
# Abstract: Returns number of tweets for that account
#----------------------------------------------------
def getTweetsAmmount(soup):
	number=''
        As= soup.findAll('a')
        for a in As:
                if a.has_attr('class'):
                        if 'ProfileNav-stat' in a['class'] and 'js-nav' in a['class']:
                                aDict = a.attrs #this is a dictionary
                                number = aDict.get('title') #gets the value for title
				number = number.split(" ", 1)
				number = number[0]
	if number == '':
		number= 'unknown'
	return number

#----------------------------------------------------
# Name: getTweetLis
# Params: Accepts soup for 1 twitter handle

#----------------------------------------------------
# Name: getTweetLis
# Params: Accepts soup for 1 twitter handle
# Abstract: Returns Li's convitaining tweets for the specified twitter handle
#----------------------------------------------------
def getTweetLis(soup):
	tweetLis= ['N/A']
        tweetFound = False
        lis = soup.findAll('li')
        for li in lis:
                if li.has_attr('class'):
                        if 'stream-item' in li['class']:
                                if tweetFound == False:
                                        tweetFound = True
                                        tweetLis.pop(0)
                                tweetLis.append(li)
        return tweetLis
        

#----------------------------------------------------
# Name: tweetType
# Params: Accepts 1 li tag
# Abstract: Returns tweet type
#----------------------------------------------------
def tweetType(li):
	if li == 'N/A':
		return li
        divs= li.findAll('div')
        for div in divs:
                if div.has_attr('data-retweet-id'):
                        return "Retweet"
        for div in divs:
                if div.has_attr('class'):
                        if 'QuoteTweet' in div['class']:
                                return 'Quote'
        allAs = li.findAll('a')
        for div in divs:
                if div.has_attr('class'):
                        if 'withheld-tweet' in div['class']:
                                return 'WithheldTweet'
        for a in allAs:
                if a.has_attr('class'):
                        if 'twitter-atreply' in a['class']:
                                return "Reply"
        return "Tweet"
 
#----------------------------------------------------
# Name: getTimeStamp
# Params: Accepts 1 li tag
# Abstract: Returns tweet timestamp for li param
#----------------------------------------------------
def getTimeStamp(li):
	if li == 'N/A':
                return li
        allAs= li.findAll('a')
        for a in allAs:
                if a.has_attr('class'):
                        if 'tweet-timestamp' in a['class']:
                                aDict = a.attrs #this is a dictionary
                                timestamp = aDict.get('title') #gets the value for title
                                return timestamp


#----------------------------------------------------
# Name: tweetID
# Params: Accepts 1 li tag
# Abstract: Returns tweet ID
#----------------------------------------------------
def getTweetID(li):
	if li == 'N/A':
                return li
        tweetID = 'N/A'
        divs = li.findAll('div')
        for div in divs:
                if div.has_attr('class'):
                        if 'original-tweet' in div['class']:
                                divDict = div.attrs #this is a dictionary
                                tweetID = divDict.get('data-tweet-id') #gets the value
                                tweetID = str(tweetID)
        return tweetID
     

#----------------------------------------------------
# Name: getTweetText
# Params: Accepts 1 li tag
# Abstract: Returns tweet text
#----------------------------------------------------
def getTweetText(li):
	if li == 'N/A':
                return li
        ps = li.findAll('p')
        content = ''
        for p in ps:
                if p.has_attr('class'):
                        if 'tweet-text' in p['class']:
                                for contentItem in p.contents:
                                        filteredContent= re.sub(r"<.*?>", "", str(contentItem))
                                        filteredContent= re.sub(r"\n", "<newline>", str(filteredContent))
                                        filteredContent= re.sub(r'"', "<quote>", str(filteredContent))
                                        content= content + filteredContent
        return content
        

#----------------------------------------------------
# Name: getTweetUrl
# Params: Accepts 1 li tag
# Abstract: Returns url for retweets and quotes
#----------------------------------------------------
def getTweetUrl(li):
	if li == 'N/A':
                return li
        tweetKind = tweetType(li)
        tweetUrl = 'N/A'
        if tweetKind == 'Retweet':
                allAs= li.findAll('a')
                for a in allAs:
                        if a.has_attr('class'):
                                if 'tweet-timestamp' in a['class']:
                                        aDict = a.attrs #this is a dictionary
                                        tweetUrl = aDict.get('href') #gets the value for title
        if tweetKind == 'Quote':
                divs = li.findAll('div')
                for div in divs:
                        if div.has_attr('class'):
                                if 'QuoteTweet-innerContainer' in div['class']:
                                        divDict = div.attrs
                                        tweetUrl = divDict.get('href')
        return tweetUrl
        

#----------------------------------------------------
# Name: getHandle
# Params: Accepts 1 li tag
# Abstract: Returns handle for retweet original and quotes
#----------------------------------------------------
def getHandle(li):
	if li == 'N/A':
                return li
        tweetKind = tweetType(li)
        tweetHandle = 'N/A'
        if tweetKind == 'Retweet':
                divs = li.findAll('div')
                for div in divs:
                        if div.has_attr('class'):
                                if 'original-tweet' in div['class']:
                                        divDict = div.attrs #this is a dictionary
                                        tweetHandle = divDict.get('data-screen-name') #gets the value 
        if tweetKind == 'Quote':
                divs = li.findAll('div')
                for div in divs:
                        if div.has_attr('class'):
                                if 'QuoteTweet-innerContainer' in div['class']:
                                        divDict = div.attrs
                                        tweetHandle = divDict.get('data-screen-name')
        if tweetKind == 'Reply':
                divs = li.findAll('div')
                for div in divs:
                        if div.has_attr('class'):
                                if 'js-profile-popup-actionable' in div['class']:
                                        divDict = div.attrs
                                        tweetHandle = divDict.get('data-mentions')
        return tweetHandle

#----------------------------------------------------
# Name: getLanguages
# Params: Accepts 1 li tag
# Abstract: Returns language of tweet
#----------------------------------------------------
def getLanguage(li):
	if li == 'N/A':
                return li
	lang = ''
        ps = li.findAll('p')
        for p in ps:
                if p.has_attr('lang'):
                        pattrs = p.attrs
                        lang = (pattrs.get('lang'))
			break
	if lang == '':
		lang = 'N/A'
	return lang
	

#----------------------------------------------------
# Name: getReplies
# Params: Accepts 1 li tag
# Abstract: Returns number of replies for li param
#----------------------------------------------------
def getReplies(li):
	if li == 'N/A':
                return li
	replies = ''
        pattern1 = re.compile('.*repl.*')
        spans = li.findAll('span')
        for span in spans:
                if span.has_attr('class'):
                        if 'ProfileTweet-actionCountForAria' in span['class'] and pattern1.match(span.contents[0]):
                                replies = span.contents[0]
                                replies = replies.rsplit(' ',1)[0]
                       		break
	if replies == '':
		replies = 'N/A'
	return replies 
      

#----------------------------------------------------
# Name: getRetweets
# Params: Accepts 1 li tag
# Abstract: Returns number of retweets for li param
#----------------------------------------------------
def getRetweets(li):
	if li == 'N/A':
                return li
	retweets = ''
        pattern1 = re.compile('.*retw.*')
        spans = li.findAll('span')
        for span in spans:
                if span.has_attr('class'):
                        if 'ProfileTweet-actionCountForAria' in span['class'] and pattern1.match(span.contents[0]):
                                retweets = span.contents[0]
                                retweets = retweets.rsplit(' ',1)[0]
				break
	if retweets == '':
		retweets = 'N/A'
	return retweets


#----------------------------------------------------
# Name: getLikes
# Params: Accepts 1 li tag
# Abstract: Returns number of likes for li param
#----------------------------------------------------
def getLikes(li):
	if li == 'N/A':
                return li
	likes = ''
        pattern1 = re.compile('.*like.*')
        spans = li.findAll('span')
        for span in spans:
                if span.has_attr('class'):
                        if 'ProfileTweet-actionCountForAria' in span['class'] and pattern1.match(span.contents[0]):
                                likes = span.contents[0]
                                likes = likes.rsplit(' ',1)[0]
				break
	if likes == '':
		likes = 'N/A'
	return likes


