#!/usr/bin/python
# coding: utf-8

import json
import os
import sys

# Opens tweets.txt to use as 'data'
data = []
with open(sys.argv[1]) as f:   
    for line in f:
        data.append(json.loads(line))    # Decode JSON to Python

# Setup for output		
uni_track = 0    # Unicode tracker
ft1 = open(sys.argv[2], 'a')   # Creates appendable ft1.txt

tweet_text = []
for i in range(0, len(data), 1):    # Convert unicode to ascii
    tweet_text = data[i].get('text')
    tweet_time = data[i].get('created_at')
    
    try:
        tweet_text = tweet_text.encode('ascii','replace')    # Encode to ascii
    except AttributeError:
        continue
    
    if "??" in tweet_text:   #If tweet contains Unicode
        tweet_text = tweet_text.replace("\/","/").replace("?","").replace("\n"," ").replace("\r"," ").replace("\t","")  # Replace characters
        uni_track = uni_track+1
    
    ft1.writelines([tweet_text, " (timestamp:", tweet_time +")" + '\n'])    # Write to file
    
ft1.write('\n' + str(uni_track) + " tweets that contained unicode.")    # Write to file unicode tracker
ft1.close()
