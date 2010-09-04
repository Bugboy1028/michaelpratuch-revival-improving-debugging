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

import string

def start():
    print "Module to show user statistics..."
    return stats_parser


def stats_parser(message, sendMessage, dbaccess):
    if message["type"] == "PRIVMSG":
        command = string.lower(string.split(message["text"], " ")[0])
        if command == "!help" \
           and len(string.split(message["text"])) == 1:
            sendMessage("!STAT <USERNAME>: Show some statistics " + \
                        "for a chat-nickname", message["sender"])
        elif command == "!stat":
            if message["receiver"][0] == "#":
                response = message["receiver"]
            else:
                response = message["sender"]
            if len(string.split(message["text"])) != 2:
                sendMessage(message["sender"] + ": Syntax Error! " + \
                            "Please try !STAT <USERNAME>", response);
            else:
                nickname = string.split(message["text"])[1]
                buildStats(sendMessage, dbaccess, nickname, response)


def buildStats(sendMessage, dbaccess, nickname, response):
    try:
        con = dbaccess()
        cursor = con.cursor()
        rows_res = cursor.execute("SELECT COUNT(*) " + \
                                  " FROM chatlog WHERE UPPER(sender) = ?",
                              (string.upper(nickname),)).fetchall()
        if len(rows_res) is not 1:
            sendMessage("Sorry, there is a problem by query the database")
        elif rows_res[0][0] == 0:
            sendMessage("Sorry, I have no stats for %s" % (nickname), response)
        else:
            print "Searching....."
            lines = rows_res[0][0]
            print "lines: %i" % (lines)
            all_res = cursor.execute("SELECT textmes FROM chatlog WHERE " + \
                                     "type = ? AND UPPER(sender) = ?", \
                                     ("PRIVMSG", \
                                      string.upper(nickname),)).fetchall()
            print "after select..."
            smiley_counter = 0
            words_per_line = 0
            for line in all_res:
                for smiley in \
                    ("^^", "^ ^", ":)", ":(", ";)", ";(", "Oo", "oO", \
                     "O o", "o O", "o_O", "O_o", ":-)", ":-(", ";-)", \
                     ";-(", ":o)", ":o(", ";o)", ";o("):
                    if smiley in line[0]:
                        smiley_counter = smiley_counter + 1
                words_per_line = words_per_line + len(string.split(line[0]))
            line_perc = float(smiley_counter) / float(lines) * 100
            sendMessage("%s wrote %i lines and used %i smileys (%i %%). " \
                        "Avg. %i words in each line." \
                        % (nickname, lines, smiley_counter, line_perc, \
                           words_per_line / lines), response)
        dbaccess("release")
    except Exception, e:
        dbaccess("release")
        raise
                
