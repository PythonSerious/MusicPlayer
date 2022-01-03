import lyricsgenius
import re
import json
from termcolor import colored
import threading
import requests
import subprocess as sp



class lyrics:
    def __init__(self, window=None, console=False):
        self.window = window  # assign current GUI for editing.
        self.console = console

    def lyric(self, query):
        try:

            def get_lyrics(searchquery):
                url = "https://evan.lol/lyrics/search/top?q=" + searchquery
                r = requests.get(url)
                jsonReturn = r.json()
                return jsonReturn['lyrics']

            querystring = query

            def removeparenthcont(test_str):  # remove "()" "[]" "{}" and the content inside.
                ret = ''
                skip1c = 0
                skip2c = 0
                for i in test_str:
                    if i == '[':
                        skip1c += 1
                    elif i == '(':
                        skip2c += 1
                    elif i == ']' and skip1c > 0:
                        skip1c -= 1
                    elif i == ')' and skip2c > 0:
                        skip2c -= 1
                    elif skip1c == 0 and skip2c == 0:
                        ret += i
                return ret

            querystring = removeparenthcont(querystring)
            if "ft" in querystring.lower():
                querystring = str(querystring).lower().split("ft")
                querystring = querystring[0]
            querystring = str(querystring).lower().replace("lyrics", "")
            querystring = str(querystring).lower().replace("music video", "")
            querystring = str(querystring).lower().replace("official audio", "")
            querystring = str(querystring).lower().replace("official video", "")
            querystring = str(querystring).lower().replace("audio", "")
            if not self.console:
                lyrics = str(get_lyrics(str(querystring)))
                import os
                with open('lyrictmp/display.txt', 'w', encoding="utf-8") as f:
                    f.write(lyrics)
                    f.close()
                programName = "notepad.exe"
                fileName = "lyrictmp/display.txt"
                sp.Popen([programName, fileName])
                return

            elif self.console:
                lyrics = str(get_lyrics(str(querystring)))
                import os
                with open('lyrictmp/display.txt', 'w', encoding="utf-8") as f:
                    f.write(lyrics)
                    f.close()
                programName = "notepad.exe"
                fileName = "lyrictmp/display.txt"
                sp.Popen([programName, fileName])
                return

        except Exception as err:
            if "TypeError: 'NoneType' object is not iterable" in str(err):
                return colored("No current song!", 'yellow')
            elif "lyrics" in str(err):
                return "No lyrics"
