#!/usr/bin/python
#============================================================================== 
# File:         getElements.py         
# Date:         Tue Feb 21 13:21:46 EST 2017
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
# Name: getJoinDate
# Params: Accepts soup for 1 twitter handle
# Abstract: Returns date the user joined twitter
#----------------------------------------------------
def getJoinDate(soup):
        spans= soup.findAll('span')
        for s in spans:
                if s.has_attr('class'):
                        if 'ProfileHeaderCard-joinDateText' in s['class']:
                                sDict = s.attrs #this is a dictionary
                                joindate = sDict.get('title') #gets the value for title
                                return joindate

#----------------------------------------------------
# Name: getTweetLis
# Params: Accepts soup for 1 twitter handle
# Abstract: Returns Li's convitaining tweets for the specified twitter handle
#----------------------------------------------------
def getTweetLis(soup):
        allDivs = soup.findAll('div')

        #returns div class="ProfileTimeline"
        for div in allDivs:
                if div.has_attr('class'):
                        if 'ProfileTimeline' in div['class']:
                                timelineDiv = div
        #returns div class='content-main' for advanced search page
                        elif 'content-main' in div['class']:
                                timelineDiv = div

        #returns div class="stream-container""
        timelineSubDivs= timelineDiv.findAll('div')
        for div in timelineSubDivs:
                if div.has_attr('class'):
                        if 'stream-container' in div['class']:
                                streamContainer = div

        #returns ol class="stream-items
        ols = streamContainer.findAll('ol')
        for ol in ols:
                if ol.has_attr('id'):
                        if 'stream-item' in ol['id']:
                                tweetList = ol

        #returns ALL li class="js-stream-item
        tweetLis= []
        lis = tweetList.findAll('li')
        for li in lis:
                if li.has_attr('class'):
                        if 'stream-item' in li['class']:
                                tweetLis.append(li)
        return tweetLis
        

#----------------------------------------------------
# Name: tweetType
# Params: Accepts 1 li tag
# Abstract: Returns tweet type
#----------------------------------------------------
def tweetType(li):
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
        tweetID = ''
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
        ps = li.findAll('p')
        content = ''
        for p in ps:
                if p.has_attr('class'):
                        if 'tweet-text' in p['class']:
                                for contentItem in p.contents:
                                        filteredContent= re.sub(r"<.*?>", "", str(contentItem))
                                        filteredContent= re.sub(r"\n", "<newline>", str(filteredContent))
                                        content= content + filteredContent
        return content
        

#----------------------------------------------------
# Name: getTweetUrl
# Params: Accepts 1 li tag
# Abstract: Returns url for retweets and quotes
#----------------------------------------------------
def getTweetUrl(li):
        tweetKind = tweetType(li)
        tweetUrl = ''
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
        tweetKind = tweetType(li)
        tweetHandle = ''
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
        ps = li.findAll('p')
        for p in ps:
                if p.has_attr('lang'):
                        pattrs = p.attrs
                        return (pattrs.get('lang'))
                #else:
                        #return 'N/A'


#----------------------------------------------------
# Name: getReplies
# Params: Accepts 1 li tag
# Abstract: Returns number of replies for li param
#----------------------------------------------------
def getReplies(li):
        pattern1 = re.compile('.*repl.*')
        spans = li.findAll('span')
        for span in spans:
                if span.has_attr('class'):
                        if 'ProfileTweet-actionCountForAria' in span['class'] and pattern1.match(span.contents[0]):
                                replies = span.contents[0]
                                replies = replies.rsplit(' ',1)[0]
                                return replies
                        #else:
                        #       return 'N/A'
                        
      

#----------------------------------------------------
# Name: getRetweets
# Params: Accepts 1 li tag
# Abstract: Returns number of retweets for li param
#----------------------------------------------------
def getRetweets(li):
        value = 'test'
        pattern1 = re.compile('.*retw.*')
        spans = li.findAll('span')
        for span in spans:
                if span.has_attr('class'):
                        if 'ProfileTweet-actionCountForAria' in span['class'] and pattern1.match(span.contents[0]):
                                retweets = span.contents[0]
                                retweets = retweets.rsplit(' ',1)[0]
                                return retweets


#----------------------------------------------------
# Name: getLikes
# Params: Accepts 1 li tag
# Abstract: Returns number of likes for li param
#----------------------------------------------------
def getLikes(li):
        pattern1 = re.compile('.*like.*')
        spans = li.findAll('span')
        for span in spans:
                if span.has_attr('class'):
                        if 'ProfileTweet-actionCountForAria' in span['class'] and pattern1.match(span.contents[0]):
                                likes = span.contents[0]
                                likes = likes.rsplit(' ',1)[0]
                                return likes
#                       else:
#                                return 'N/A'


