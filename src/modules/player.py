import time
import vlc
from modules.query import searcher
import sys
import asyncio
from termcolor import colored
import threading

querySearcher = searcher()


class player:
    def __init__(self, window=None, console=False, print_event=None):
        self.player = None
        self.current = None
        self.queue = None
        self.window = window
        self.paused = False
        self.console = console
        self.print_event = print_event
    # write queue system.
    # Event Functions

    async def generatePlayer(self, media=None, fromQueue=False, trackattrs=None, originLink = None):
        if fromQueue is True:
            trackattr = self.queue[0]['title']
            LocalInstance = vlc.Instance('--no-xlib --quiet')

            link = await querySearcher.querySearch(self.queue[0]["URL"])
            link = link[0]
            self.player = LocalInstance.media_player_new(link)
            events = self.player.event_manager()
            events.event_attach(vlc.EventType.MediaPlayerEndReached, self.SongFinished, 1)
            self.queue.remove(self.queue[0])
            self.player.play()
            self.current = trackattr
            if not self.console:
                self.print_event(f"[{colored('EVENT', 'yellow')}] Started playing: {colored(trackattr, 'magenta')} from queue.")

            if self.paused is None or self.paused is True:
                self.paused = False

            if not self.console:
                await self.viewQueue()

            elif self.console:
                return f'Currently Playing: {trackattr}.'
        elif fromQueue is False:
            LocalInstance = vlc.Instance('--no-xlib --quiet')
            localPlayer = LocalInstance.media_player_new(str(media))  # init the audio player with VLC
            self.player = localPlayer
            localPlayer.play()
            self.current = trackattrs
            if self.paused is None or self.paused is True:
                self.paused = False
            events = localPlayer.event_manager()
            events.event_attach(vlc.EventType.MediaPlayerEndReached, self.SongFinished, 1)
            if not self.console:
                self.window.find_element("CurrentPlayer").Update(f'Currently Playing: {trackattrs}.')
            elif self.console:
                return f"Currently Playing: {trackattrs}"


    def SongFinished(self, event, param):
        if (self.queue != None) and not self.queue == []: # Check if self.queue is NoneType or an empty array.

                self.print_event(f"[{colored('EVENT', 'yellow')}] {colored(f'{self.current}', 'magenta')} ended.")
                asyncio.run(self.generatePlayer(fromQueue=True))
                self.window.find_element("CurrentPlayer").Update(f'Currently Playing: {self.current}.')
        else:
            if not self.console:
                self.window.find_element("StatusBox").Update('Stopped.')
                self.window.find_element("CurrentPlayer").Update(f'')
                self.print_event(f"[{colored('EVENT', 'yellow')}] Queue ended.")
                self.queue = None
                self.player = None
            elif self.console:
                import modules.console
                console = modules.console.console()
                console.intro()
                print("End of queue.")
                self.player = None
                console.printOptions()


    async def viewQueue(self):
        if self.queue is None:
            if not self.console:
                self.window.find_element("BoxArea").Update(f"Queue:\n\nThe queue is empty; add some songs!")
            elif self.console:
                raise Exception("There is no queue!")
        else:
            formatList = []
            for x in range(0, len(self.queue)):
                item = self.queue[x]
                formatString = f"{x + 1}. {item['title']}"
                formatList.append(formatString)
            if not formatList == []:
                finalFormat = "\n".join(formatList)
            else:
                finalFormat = f"The queue is empty; add some songs!"
            if not self.console:
                self.window.find_element("BoxArea").Update(f"Queue:\n\n{finalFormat}")
            elif self.console:
                return f"Queue:\n\n{finalFormat}"
            return

    async def skip(self):
        if self.player is None:
            return "No player"
        elif self.player is not None:
            if self.queue is not None and not self.queue == []:
                await self.stop(changeQueue=False)
                await self.generatePlayer(fromQueue=True)
                await self.viewQueue()
                if not self.console:
                    self.window.find_element("CurrentPlayer").Update(f'Currently Playing: {self.current}.')
                    self.window.find_element("StatusBox").Update('Skipped.')
                    self.print_event(f"[{colored('COMMAND', 'cyan')}] Skipped track.")

                elif self.console:
                    return "Skipped."

        else:
            def set_par():
                self.window.find_element("StatusBox").Update('Playing.')

            if not self.console:
                threading.Timer(1.5, set_par).start()
                self.window.find_element("StatusBox").Update('No songs in the queue!')
            elif self.console:
                import main
                main.intro()
                return "End of Queue."
            await self.viewQueue()

    async def play(self, link, originLink=None, trackattrs=None):
        if self.player is None:
            LocalInstance = vlc.Instance('--no-xlib --quiet')
            self.player = LocalInstance.media_player_new()
            events = self.player.event_manager()
            events.event_attach(vlc.EventType.MediaPlayerEndReached, self.SongFinished, 1) # Hook the track events.
            media = LocalInstance.media_new(link) # Add the audio.
            self.player.set_media(media)
            self.player.play()


            self.current = trackattrs

            if self.paused is None or self.paused is True:
                self.paused = False

            if not self.console:
                self.window.find_element("CurrentPlayer").Update(f'Currently Playing: {trackattrs}.')
                self.print_event(f"[{colored('COMMAND', 'cyan')}] Started playing: {colored(trackattrs, 'magenta')}")
            elif self.console:
                return f"Currently Playing: {trackattrs}"
            return ""



        else:
            if self.queue is None:
                self.queue = []
                self.queue.append({"title": trackattrs, "URL": str(originLink)})
                self.print_event(f"[{colored('COMMAND', 'cyan')}] Queued: {colored(trackattrs, 'magenta')} Position: {len(self.queue)}")
                await self.viewQueue()
                return f"Added {trackattrs} to the queue"
            else:
                self.queue.append({"title": trackattrs, "URL": str(originLink)})

                self.print_event(f"[{colored('COMMAND', 'cyan')}] Queued: {colored(trackattrs, 'magenta')} Position: {len(self.queue)}")
                await self.viewQueue()
                return f"Added {trackattrs} to the queue"


    async def pause(self):
        if self.player is None:
            return "No player"
        else:
            self.paused = not self.paused
            self.player.pause()
            if self.console:
                if self.paused is True:
                    return "Paused."
                elif self.paused is False:
                    return "Playing."
            async def set_par():
                if self.paused is True:
                    self.window.find_element("StatusBox").Update('Paused.')
                    self.print_event(f"[{colored('COMMAND', 'cyan')}] Paused track.")

                elif self.paused is False:
                    self.window.find_element("StatusBox").Update('Playing.')
                    self.print_event(f"[{colored('COMMAND', 'cyan')}] Resumed track.")


            await set_par()

    async def stop(self, changeQueue = True):
        if not self.console and changeQueue:
            self.window.find_element("StatusBox").Update('Stopped.')

        if self.player is None:
            return "No player"
        else:
            self.player.stop()
            if not self.console:
                self.window.find_element("CurrentPlayer").Update(f' ')
                self.window.find_element("BoxArea").Update(f' ')
            if changeQueue:
                if not self.console:
                    self.print_event(f"[{colored('COMMAND', 'cyan')}] Stopped track and cleared queue.")
                self.queue = None
            self.player = None
            if self.console:
                return "Stopped audio."


    async def volume(self, amount=None):
        if amount is None:
            return "No volume selected"
        else:
            if self.player is None:
                return "No player"
            else:
                self.player.audio_set_volume(amount)
                if self.console:
                    return f"Volume set to {amount}"
                elif not self.console:
                    self.print_event(f"[{colored('COMMAND', 'cyan')}] Volume set to: {amount - 30}") # Subtract difference for the player range
