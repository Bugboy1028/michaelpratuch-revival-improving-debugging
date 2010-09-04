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

"""
This is a small plugin which does only tell the server's time
It takes a few comments to show how plugins work
"""


""" Importing Modules. This is python-stuff """
import string
import datetime

"""
Every plugin must contain a start()-Method.
It will be called during the bot's startup and must return a method 
which needs 3 arguments
"""
def start():
    print "Plugin to tell the users the server's time"
    return timep


"""
This is the loop-method. The start-method will return this method.
It needs following arguments:
message = a directory which has following keys:
          message["time"] - System time of the message
          message["sender"] - nickname which send the message
          message["shost"] - the senders host
          message["type"] - type of he message
          message["receiver"] - the receiver of the message
                                #room or user
          message["text"] - the message's text
sendMessage = is a Method. Call it to send messages to the chat:
              def sendMessage(text, receiver, msgtype="PRIVMSG"):  
              text - The message to send (string)
              receiver - The receiver (#room or user)
              msgtype - PRIVMSG if not set. Use SYSTEM to send high priority
                        messages like WHOIS-querys. Note: you must completely
                        write in the text. They will be send without
                        any change, if you use "SYSTEM"
dbaccess = The databse interface. Take a look to some other plugins to 
           see it working
           
Note: you should use this parameter-names and there order and take it as
convention.
"""
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



