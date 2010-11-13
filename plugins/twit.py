"""
Isidore - Python IRC Bot

Copyright (C) 2010 Sebastian Meyer (s.meyer@drachenjaeger.eu)

This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this 
program; if not, see <http://www.gnu.org/licenses/>
"""

import json
import urllib
import string
import datetime

if __name__ != "__main__":
    import bot
    # room where the bot should talk to
    room = "#" + bot.room

# Search-Options for the twitter search-url
urloptions = "q=radiotux+-from%3Aradiotux+-to%3Aradiotux"
# urloptions = "q=%23wikipedia"
# twitter-search-url
twitterurl = "http://search.twitter.com/search.json?"
# seconds between 2 searchen on twitter
secwait = 500

maxid = 0

def start():
    print "Plugin to get informations from twitter..."
    # getting the tweets before starting to get the maxid, not flood the room
    getTweets()
    return twit_parser

def settimer():
    timer = { "function" : twit_timer, "seconds" : secwait }
    return (timer, )

def twit_timer(sendMessage, dbaccess):
    print "Twitter Timer runs..."
    tweets = getTweets()
    if len(tweets) > 0:
        if len(tweets) == 1:
            sendMessage("Hey, found a tweet that might interest you.", \
                        room)
        else:
            sendMessage("Hey, found some tweets that might " \
                        "interest you.", room)
        for tweet in tweets:
            tweet["text"] = string.replace(tweet["text"], "\n", "")
            sendstr = "From twitter: %s wrote %s: %s" \
                    % (tweet["from_user"], \
                       tweet["created_at"][:-6], \
                       tweet["text"])
            sendMessage(sendstr.encode("utf-8"), room)


def twit_parser(message, sendMessage, dbaccess):
    if message["type"] == "PRIVMSG" and message["text"][0] == "!":
        command = string.split(message["text"], " ")[0]
        if string.lower(command) == "!twitter":
            sendTweets(message, sendMessage)
        elif string.lower(command) == "!help" \
             and len(string.split(message["text"], " ")) == 1:
            sendMessage("!TWITTER: shows some interesting " \
                        "tweets (max. 3 inside a room, " \
                        "20 inside a query)", message["sender"])


def sendTweets(message, sendMessage):
    if message["receiver"][0] == "#":
        response = message["receiver"]
        maxcount = 3
    else:
        response = message["sender"]
        maxcount = 20
    tweets = getTweets(allover=True)
    for tweet in tweets[:maxcount]:
        print "Sende einen tweet: " + str(tweet)
        tweet["text"] = string.replace(tweet["text"], "\n", "")
        sendstr = "From twitter: %s wrote %s: %s" \
                    % (tweet["from_user"], \
                       tweet["created_at"][:-6], \
                       tweet["text"])
        sendMessage(sendstr.encode("utf-8"), response)

    
def getTweets(allover=False):
    global maxid
    urlstring = twitterurl+urloptions
    if allover == False:
        urlstring = urlstring + "&since_id="+str(maxid)
    print "Getting Tweets from URL:" + urlstring
    u = urllib.urlopen(urlstring)
    j = json.load(u)
    tweets = j["results"]
    if allover == False:
        for tweet in tweets:
            if tweet["id"] > maxid:
                maxid = tweet["id"]
        # maxid = j["max_id"]
    return tweets


if __name__ == "__main__":
    for tweet in getTweets():
        print "---"
        print tweet["from_user"]
        print tweet["created_at"]
        text = string.replace(tweet["text"], "\r", "")
        text = string.replace(text, "\n", "")
        print text.encode("utf-8")

