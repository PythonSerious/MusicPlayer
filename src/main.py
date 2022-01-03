# Main file we will install all the modules here
# We will use OS in this case to install any modules that we need that are not already installed.
import asyncio
import os
import sys

os.add_dll_directory(os.getcwd())



os.system('mode con: cols=122 lines=19') # Set terminal window size

# Check if the argument is --console if so make sure it runs console mode.

consoleRun = False

exeloc = str(sys.executable)

if len(sys.argv) > 1:
    if sys.argv[1] == "--console":
        consoleRun = True
    elif sys.argv[1] == "--fresh": # Uninstalls all used modules to simulate a fresh install.
        os.system(f"{exeloc} -m pip uninstall pysimplegui")
        os.system(f"{exeloc}-m pip uninstall yt-dlp")
        os.system(f"{exeloc} -m pip uninstall spotipy")
        os.system(f"{exeloc} -m pip uninstall youtube-search-python")
        os.system(f"{exeloc} -m pip uninstall python-vlc")
        os.system(f"{exeloc} -m pip uninstall lyricsgenius")
        os.system(f"{exeloc} -m pip uninstall termcolor")
        print("All modules uninstalled; re-run for fresh install.")
        exit(1)
    else:
        print("Invalid option. Available options: [--console (run console based)]")
        exit()

try:
    # Attempt to import all the modules we will use.
    import PySimpleGUI
    import yt_dlp
    import spotipy
    import youtubesearchpython
    import vlc
    import lyricsgenius
    import termcolor
    import bs4
    import lxml

except Exception as err:
    print(err)
    # We'll install the requirements.txt file again.
    try:
        os.system(f"{exeloc} -m pip install -r \"requirements.txt\"")
    except:
        os.system(f"{exeloc} -m pip install --upgrade pip")
        os.system(f"{exeloc} -m pip install -r \"requirements.txt\"")
    print("Installed requirements.")

import modules.query

query = modules.query.searcher()
from modules.player import player
from modules.window import window
import modules.console
if consoleRun:
    console = modules.console.console()
    console.intro()
    asyncio.run(console.console(player=player(console=True)))
elif not consoleRun:
    windowClass = window()
    asyncio.run(windowClass.window())
