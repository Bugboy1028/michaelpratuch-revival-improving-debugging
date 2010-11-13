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

""" Wanna have som drinks??? """

import string
import random

drinks = ("bier", "scotch", "bourbon", "wodka", \
          "champagner", "limonade", "cola", \
          "beer", "whiskey", "kaffee", "mate",
          "tee", "tea", "coffee",)

answers = (\
          "brings some [DRINK] to [RECEIVER]",
          "loots the bar and brings [RECEIVER] a [DRINK]",
          "renames the channel to #MoesTavern " + \
             "and brings [RECEIVER] some [DRINK]",
          )

def start():
    print "Drink module..."
    return drink_parser

def drink_parser(message, sendMessage, dbaccess):
    if message["type"] == "PRIVMSG":
        text = message["text"]
        if string.lower(string.split(text, " ")[0]) == "!help" \
           and len(string.split(text, " ")) == 1:
            sendMessage("!<SomeDrink> [Receiver] : " + \
                        "use the bot as steward", message["sender"])
        elif text[0] == "!":
            command = string.split(text, " ")[0]
            if string.lower(command[1:]) in drinks:
                response = message['reply']
                bringdrink(command[1:], message["sender"],\
                           text, response, sendMessage)


def bringdrink(drink, sender, text, response, sendMessage):
    if len(string.split(text, " ")) == 1:
        drinkReceiver = sender
    else:
        drinkReceiver = string.split(text, " ")[1]
    r = random.randint(0, len(answers) - 1)
    toSend = answers[r]
    toSend = string.replace(toSend, "[DRINK]", drink)
    toSend = string.replace(toSend, "[RECEIVER]", drinkReceiver)
    toSend = u"\u0001ACTION " + toSend + u"\u0001"
    sendMessage(text = toSend, receiver = response)
    
