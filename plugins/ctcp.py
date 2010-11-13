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
This plugin will response to CTCP-Version callings.
It returns a string with a short text
"""

import sys
import bot

def start():
    print "Module to handle CTCP-requests ..."
    return ctcpfunc

def ctcpfunc(message, sendMessage, dbaccess):
    # response to VERSION querys
    if message["text"] == u"\u0001VERSION\u0001":
        bv = bot.version
        sendMessage(text = u"\u0001VERSION Isidore-IRC-Bot - " \
                    u"Version: %s.%s.%s - " \
                    u"(http://code.google.com/p/isidore/)\u0001" \
                    % (bv["major"], bv["minor"], bv["subbuild"]), \
                     receiver = message["sender"], 
                     msgtype="NOTICE")
    #response to PING querys
    elif message["text"].startswith(u"\u0001PING"):
        sendMessage(text = message["text"], 
                    receiver = message["sender"],
                    msgtype="NOTICE")

