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
import urllib
import xml.dom.minidom as dom

def start():
    print "Weather module..."
    return weather_parser


def weather_parser(message, sendMessage, dbaccess):
    if message["type"] == "PRIVMSG":
        command = string.split(message["text"], " ")[0]
        if len(string.split(message["text"], " ")) == 1:
            if string.lower(command) == "!help":
                sendMessage("!WEATHER <CITY> : Tells you some informations " + \
                           "about the weather in <CITY>", message["sender"])
            elif string.lower(command) == "!weather" \
                 or string.lower(command) == "!wetter":
                response = message["reply"]
                sendMessage(message["sender"] + ": <SyntaxError>: " + \
                           "try: !WEATHER <CITY>", response)
        elif string.lower(command) == "!weather" \
             or string.lower(command) == "!wetter":
            parseText(message, sendMessage)
        

def parseText(message, sendMessage):
    response = message["reply"]
    village = message["text"][string.index(message["text"], " "):]
    text = getWeather(village)
    sendMessage(message["sender"] + ": " + text, response)
    

def getWeather(village):
    try:
        params = urllib.urlencode({'weather': village})
        f = urllib.urlopen("http://www.google.com/ig/api?%s" % params)
        content = f.read()
        tree = dom.parseString(content.decode('latin-1').encode('utf-8'))
        fc_ele = tree.firstChild
        weather_ele = fc_ele.getElementsByTagName("weather")[0]
        forecast_ele = fc_ele.getElementsByTagName("forecast_information")[0]
        city_ele = fc_ele.getElementsByTagName("city")[0]
        city = city_ele.getAttribute("data")
        curcond_ele = weather_ele.getElementsByTagName("current_conditions")[0]
        temp_ele = curcond_ele.getElementsByTagName("temp_c")[0]
        temp = temp_ele.getAttribute("data")
        cond_ele = curcond_ele.getElementsByTagName("condition")[0]
        cond = cond_ele.getAttribute("data")
        humidity_ele = curcond_ele.getElementsByTagName("humidity")[0]
        humidity = humidity_ele.getAttribute("data")
        wind_ele = curcond_ele.getElementsByTagName("wind_condition")[0]
        wind = wind_ele.getAttribute("data")
        retstr = "Weather for '%s': %s degree celsius - %s - %s - %s" % \
                 (city, temp, cond, humidity, wind)
        retstr = retstr + " (data provided by google)"
        retstr = retstr.encode("utf-8")
    except Exception, e:
        if "list index out of range" in str(e):
            retstr = "Sorry, seems there are no weather-informations " + \
                     "for %s" % (village,)
        else:
            raise
    return retstr


if __name__ == "__main__":
    print "WEATHER MODULE -- Testmode"
    print getWeather("muenchen")
    
