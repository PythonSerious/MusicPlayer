import asyncio

import PySimpleGUI as sg
import modules.player
from modules.query import searcher as qs
import threading
import sys
from termcolor import colored
import os
import modules.console


class window:
    def __init__(self):
        self.player = None

    def print_event(self, toPrint = None):
        os.system('mode con: cols=122 lines=19')
        os.system('cls')
        modules.console.console.intro()
        try:
            print(f"[{colored('INFO', 'yellow')}] Currently Playing: {colored(self.player.current, 'cyan')}")
            print(f"[{colored('INFO', 'yellow')}] Queue Length: {colored(len(self.player.queue), 'cyan')}")
        except:
            pass
        print(
            f"[{colored('TIP', 'green')}] Don't like our snazzy UI? You can launch the program with the '--console' parameter to use the console based input.")
        print(toPrint)

    async def window(self):
        sg.theme('Dark Grey 6')
        layout = [[sg.Text('Audio Controls')],
                  [sg.Text('Enter a song query:'), sg.InputText()],
                  [sg.Button('Pause/Resume'), sg.Button('Start Audio'), sg.Button("Toggle Lyrics"), sg.Button("Skip"),
                   sg.Button("Stop"), sg.Text(" ", key="StatusBox")],
                  [sg.Text("Volume"),
                   sg.Slider(orientation='horizontal', key='stSlider', default_value=50, size=(20, 15), range=(0, 100),
                             enable_events=True)],
                  [sg.Text("", key="CurrentPlayer")],
                  [sg.Text("", key="BoxArea")]

                  ]


        self.print_event(f"[{colored('INFO', 'yellow')}] Launching Window.\n[{colored('INFO', 'yellow')}] Enabled event log.")


        window = sg.Window('Music Player', icon='./logo.ico', resizable=True, return_keyboard_events=True,
                           location=(250, 250)).Layout(
            layout).Finalize()
        window.Size = (500, 300)
        audioPlayer = True
        player = modules.player.player(window=window, print_event=self.print_event)
        self.player = player
        lyricson = False
        while audioPlayer:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                audioPlayer = False
                continue
            else:
                if event == "Pause/Resume":
                    await player.pause()

                if event == "stSlider":
                    await player.volume(int(values['stSlider'] + 30))


                elif event == "Start Audio":
                    searcher = qs()

                    async def toThread():
                        try:


                            self.print_event(f"[{colored('COMMAND', 'cyan')}] Querying for: \"{values[0]}\"")
                            result = await searcher.querySearch(values[0], player=player)

                            if result is None:
                                pass
                            elif result[0] == "playlist":
                                pass
                            else:
                                await player.play(*result)
                        except Exception as err:
                            raise err
                            self.print_event(f"[{colored('WARN', 'red')}] Search error: {err}")

                            async def set_par():
                                window.find_element("CurrentPlayer").Update(f'{err}')

                            await set_par()

                        async def set_par():
                            window.find_element("StatusBox").Update('Playing.')

                        await set_par()
                        paused = False

                    window.find_element("StatusBox").Update('Queueing...')

                    def between_callback():
                        asyncio.run(toThread())


                    threading.Timer(0, between_callback).start()
                    continue

                elif event == "Skip":
                    async def run():
                        await player.skip()

                    def between_callback():
                        asyncio.run(run())
                    window.find_element("StatusBox").Update('Skipping.')
                    threading.Timer(.1, between_callback).start()


                elif event == "Stop":
                    await player.stop()
                    continue
                elif event == "Toggle Lyrics":
                    def lyricrun():
                        import modules.lyrics
                        lyrics = modules.lyrics.lyrics(window)
                        self.print_event(f"[{colored('COMMAND', 'cyan')}] Fetching lyrics for: \"{player.current}\".")
                        response = lyrics.lyric(query=player.current)
                        if response == "No lyrics":
                            self.print_event(f"[{colored('WARN', 'red')}] No results found.")
                        else:
                            self.print_event(f"[{colored('EVENT', 'yellow')}] Display Lyrics.")

                    threading.Timer(0, lyricrun).start()
                    continue
                else:
                    pass
