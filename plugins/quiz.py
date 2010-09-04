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
import random

def start():
    print "Quiz Module..."
    return quiz

def sendHelp(message, sendMessage, helptype="all"):
    if message["type"] == "PRIVMSG" and \
       len(string.split(message["text"], " ")) == 1:
        sendMessage("!QUIZ <COMMAND> : Bot's quiz-function. Try !HELP QUIZ",\
                    message["sender"])
    elif message["type"] == "PRIVMSG":
        if string.lower(string.split(message["text"], " ")[1]) == "quiz":
            if helptype == "all":
                sendMessage("Some informations about the bot's quiz-function:",\
                            message["sender"])
            if helptype == "question" or helptype == "all":
                sendMessage("!QUIZ QUESTION : shows the actual question", \
                            message["sender"])
            if helptype == "answer" or helptype == "all":
                sendMessage("!QUIZ ANSWER <yourAnswer> : tell your answer", \
                            message["sender"])
            if helptype == "addquestion" or helptype == "all":
                sendMessage("!QUIZ ADDQUESTION <YourQuestion> $$ " + \
                            "<possibleAnswer> $$ <otherPossibleAnswer> " + \
                            "[$$ <otherPossibleAnswer> ...] " + \
                            "$$$ <explainTheAnswer> : add a new " + \
                            "question to the database", message["sender"])
            if helptype == "halloffame" or helptype == "all":
                sendMessage("!QUIZ HALLOFFAME : shows the Hall-Of-Fame", \
                            message["sender"])


def creaeteQuestionDatabase(cursor):
    cursor.execute("CREATE TABLE quizquestions " + \
                   "(id INTEGER PRIMARY KEY, "+ \
                   "question VARCHAR, answers VARCHAR, " + \
                   "active BOOLEAN, lastasked TIMESTAMP)")


def activateNextQuestion(message, sendMessage, cursor, response):
    result = cursor.execute("SELECT id FROM quizquestions " + \
                            "WHERE active = 'False'").fetchall()
    if len(result) == 0:
        sendMessage("QUIZ: sorry, can't find any Questions", response)
        return 1
    else:
        count = len(result)
        strike = random.randint(0, count - 1)
        idn = result[strike][0]
        cursor.execute("UPDATE quizquestions SET active = 'False' " + \
                       "WHERE active = 'True'")
        cursor.execute("UPDATE quizquestions SET active = 'True' " + \
                       "WHERE id = ?", (idn, ))
        return 0

        
def question(message, sendMessage, cursor, response):
    try:
        result = cursor.execute("SELECT question FROM " + \
                    "quizquestions WHERE active = 'True'").fetchall()
        if len(result) == 0:
            sendMessage("QUIZ: No active question found, looking " + \
                        "for a new one", response)
            nm = activateNextQuestion(message, sendMessage, cursor, response)
            if nm == 0:
                question(message, sendMessage, cursor, response)
        else:
            sendMessage("QUIZ Question is: " + result[0][0], response)
            sendMessage("QUIZ Please answer using: !QUIZ ANSWER <YourAnswer>",\
                        response) 
    except Exception, e:
        if "no such table" in str(e):
            creaeteQuestionDatabase(cursor)
            question(message, sendMessage, cursor, response)
        else:
            raise

def createPlayerDatabase(cursor):
    cursor.execute("CREATE TABLE quizhs (player VARCHAR, points INTEGER)")


def incplayerpoints(message, cursor):
    try:
        result = cursor.execute("SELECT points FROM quizhs " + \
                    "WHERE player = ?", (message["sender"],)).fetchall()
        if len(result) == 0:
            cursor.execute("INSERT INTO quizhs (player, points) " + \
                           "VALUES (?, ?)", (message["sender"], 1))
        else:
            cursor.execute("UPDATE quizhs SET points = ? WHERE " + \
                           "player = ?", (result[0][0]+1, message["sender"]))
    except Exception, e:
        if "no such table" in str(e):
            createPlayerDatabase(cursor)
            incplayerpoints(message, cursor)
        else:
            raise
        

def answer(message, sendMessage, cursor, response):
    try:
        result = cursor.execute("SELECT answers FROM quizquestions " + \
                                "WHERE active = 'True'").fetchall()
        if len(result) == 0:
            sendMessage("QUIZ: Sorry, there is no active Question",
                        response)
            sendMessage("QUIZ: Please try <!QUIZ QUESTION> or <!QUIZ HELP>",
                        response)
        else:
            answerstart = string.index(message["text"], " ", 7)
            if answerstart < 0:
                sendMessage(message["sender"] + ": QUIZ <Syntax Error>", response)
            else:
                correct = False
                given = string.strip(message["text"][answerstart:])
                right_answers = string.split(result[0][0], "$$")
                for right_answer in right_answers:
                    print "Right answer:", right_answer
                    print "Vergleich:", given
                    if string.strip(string.lower(given)) == \
                       string.strip(string.lower(right_answer)):
                        correct = True
                        break
                if correct == True:
                    sendMessage(message["sender"] + ": Yeah, that's right. " + \
                            "Congratulations!", response)
                    if len(string.split(result[0][0], "$$$")) > 1:
                        fullanswer = string.split(result[0][0], "$$$")[1]
                        sendMessage("QUIZ: Explained answer: " + fullanswer, response)
                    incplayerpoints(message, cursor)
                    activateNextQuestion(message, sendMessage, cursor, response)
                    question(message, sendMessage, cursor, response)
                else:
                    sendMessage(message["sender"] +": Sorry, that's wrong",
                                response)
    except Exception, e:
        if "no such table" in str(e):
            creaeteQuestionDatabase(cursor)
            answer(message, sendMessage, cursor, response)
        else:
            raise    


def addquestion(message, sendMessage, cursor, response):
    try:
        parts = string.split(message["text"], "$$")
        if len(parts)< 3:
            sendMessage("<Syntax Error>, please see !QUIT HELP", response)
        else:
            startq = string.index(message["text"], " ", 7)
            question = message["text"][startq : string.find(message["text"], "$$")]
            answer = message["text"][string.find(message["text"], "$$") + 2:]
            cursor.execute("INSERT INTO quizquestions (question, answers, active) " + \
                           "VALUES (?, ?, ?)", (question, answer, 'False'))
            sendMessage(message["sender"] + ": your question was " + \
                        "collected. Many thanks!", response)
    except Exception, e:
        if "no such table" in str(e):
            creaeteQuestionDatabase(cursor)
            addquestion(message, sendMessage, cursor, response)
        else:
            raise  

def halloffame(message, sendMessage, cursor, response):
    try:
        if response[0] == "#":
            maxcount = 3
        else:
            maxcount = 10
        result = cursor.execute("SELECT player, points FROM quizhs " + \
                       "ORDER BY points DESC " + \
                       "LIMIT " + str(maxcount)).fetchall()
        if len(result) == 0:
            sendMessage(message["sender"] + ": There are no entries in the HOF " + \
                        "at the moment", response)
        else:
            i = 1
            for row in result:
                sendMessage(str(i) + ". " + str(row[0]) + " has " + \
                            str(row[1]) + " points", response)
                i = i + 1
    except Exception, e:
        if "no such table" in str(e):
            createPlayerDatabase(cursor)
            halloffame(message, sendMessage, cursor, response)
        else:
            raise    


def quiz(message, sendMessage, dbaccess):
    if message["type"] == "PRIVMSG":
        # The helpt text
        if string.lower(string.split(message["text"], " ")[0]) == "!help":
            sendHelp(message, sendMessage)
        #quiz
        elif string.lower(string.split(message["text"], " ")[0]) == "!quiz":
            if message["receiver"][0] == "#":
                response = message["receiver"]
            else:
                response = message["sender"]
            if len(string.split(message["text"], " ")) == 1:
                sendMessage(message["sender"] + ": <Syntax Error>, " + \
                            "try: !HELP QUIZ", response)
            elif string.lower(string.split(message["text"], " ")[1]) in \
                    ("question", "answer", "addquestion", "halloffame"):
                command = string.lower(string.split(message["text"], " ")[1])
                con = dbaccess()
                cursor = con.cursor()
                try:
                    if command == "question":
                        question(message, sendMessage, cursor, response)
                    elif command == "answer":
                        answer(message, sendMessage, cursor, response)
                    elif command == "addquestion":
                        addquestion(message, sendMessage, cursor, response)
                    elif command == "halloffame":
                        halloffame(message, sendMessage, cursor, response)
                    con.commit()
                    con.close()
                    dbaccess("release")
                except Exception:
                    dbaccess("release")
                    raise
            else:
                sendMessage(message["sender"] + \
                            ": <Syntax Error>, try: !HELP QUIZ", response)
        
