# **PyMusicPlayer**
<img width=200px height=200px align="right" src="https://raw.githubusercontent.com/PythonSerious/MusicPlayer/main/src/logo.png">
PyMusic Player is a music player written in python3. It harvests raw youtube URL's soundcloud URL's apple music URL's and spotify.


### Installation

Python __MUST__ be added to path, or else the requirements will not be able to self install.
(gonna use sys to grab the py exe path to fix this.)

### Configuration

In order to enable spotify querys you must paste your API keys into the config.json file in /src

Paste the client token and client secret in there and it will work.


### Pictures

<img width=500px height=300px align="center" src="https://cdn.squarebot.app/python3.9_A2Tui54InJ.png">

Logger console:

<img width=800px height=300px align="center" src="https://cdn.squarebot.app/cmd_pszH5qEW3J.png">


Console Mode:
( meant for simple usage or debug. NOT pretty.)

<img width=800px height=300px align="center" src="https://cdn.squarebot.app/cmd_f1QPtKaLz6.png">





# Credits

Couldn't have made this without the following people and projects! 

- Anthony (PythonSerious) | Lead scripter/designer
- Colby | Bug Patcher / Tester
- David | Bug Patcher / Tester


Libs:


- PySimpleGUI (GUI)
- spotipy (spotify resolver)
- youtubesearchpython (searcher for yt)
- YT-DLP (Faster Youtube-dl alternative, great resource)
- BS4 (Scraper for apple music)
- VLCpython (Main handler for audio)
- LIBVLC (Actual framework for audio playing)
