"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Isidore - Python IRC Bot

Copyright (C) 2010 Sebastian Meyer (s.meyer@drachenjaeger.eu)

This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this 
program; if not, see <http://www.gnu.org/licenses/

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import string
import datetime


def start():
    print "Plugin to tell the users the server's time"
    return timep



def timep(message, sendMessage, dbaccess):
    if message["type"] == "PRIVMSG":
        if len(string.split(message["text"], " ")) == 1:
            command = string.lower(string.split(message["text"], " ")[0])
            if command == "!help":
                sendHelp(message, sendMessage)
            elif command == "!time":
                sendTime(message, sendMessage)


def sendHelp(message, sendMessage):
    sendMessage("!TIME : Show the server's time", message["sender"])
    
    
def sendTime(message, sendMessage):
    if message["receiver"][0] == "#":
        response = message["receiver"]
    else:
        response = message["sender"]
    timestring = str(datetime.datetime.now())
    sendMessage("My time is: " + timestring[:19], response)



