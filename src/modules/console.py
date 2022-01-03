from termcolor import colored
import modules.query
import os
from modules.lyrics import lyrics
import threading

class console:
    def __init__(self):
        self.running = False
        self.optiontext = "p = pause, s = skip, a = add song, q = view queue\nv = set volume, e = exit, l = get lyrics, fix = fix text"

    def intro(self=None):
        os.system("cls")
        print()
        row1 = f"{colored(' /$$$$$$$            /$$      /$$                     /$$', 'blue', attrs=['blink'])} {colored('           /$$$$$$$  /$$', 'yellow', attrs=['blink'])}"
        row2 = f"{colored('| $$__  $$          | $$$    /$$$                    |__/', 'blue', attrs=['blink'])} {colored('          | $$__  $$| $$', 'yellow', attrs=['blink'])}"
        row3t = '''| $$  \ $$ /$$   /$$| $$$$  /$$$$ /$$   /$$  /$$$$$$$ /$$  /$$$$$$$'''
        row3t2 = '''| $$  \ $$| $$  /$$$$$$  /$$   /$$  /$$$$$$   /$$$$$$'''
        row3 = f"{colored(row3t, 'blue', attrs=['blink'])} {colored(row3t2, 'yellow', attrs=['blink'])}"
        row4 = f"{colored('| $$$$$$$/| $$  | $$| $$ $$/$$ $$| $$  | $$ /$$_____/| $$ /$$_____/', 'blue', attrs=['blink'])} {colored('| $$$$$$$/| $$ |____  $$| $$  | $$ /$$__  $$ /$$__  $$', 'yellow', attrs=['blink'])}"
        row5t = "| $$____/ | $$  /$$$$$$$| $$  | $$| $$$$$$$$| $$  \__/"
        row5 = f"{colored('| $$____/ | $$  | $$| $$  $$$| $$| $$  | $$|  $$$$$$ | $$| $$      ', 'blue', attrs=['blink'])} {colored(row5t, 'yellow', attrs=['blink'])}"
        row6t = "| $$      | $$  | $$| $$\  $ | $$| $$  | $$ \____  $$| $$| $$      "
        row6 = f"{colored(row6t, 'blue', attrs=['blink'])} {colored('| $$      | $$ /$$__  $$| $$  | $$| $$_____/| $$      ', 'yellow', attrs=['blink'])}"
        row7t = "| $$      |  $$$$$$$| $$ \/  | $$|  $$$$$$/ /$$$$$$$/| $$|  $$$$$$$"
        row7 = f"{colored(row7t, 'blue', attrs=['blink'])} {colored('| $$      | $$|  $$$$$$$|  $$$$$$$|  $$$$$$$| $$      ', 'yellow', attrs=['blink'])}"
        row8t = "|__/       \____  $$|__/     |__/ \______/ |_______/ |__/ \_______/"
        row8t2 = "|__/      |__/ \_______/ \____  $$ \_______/|__/"
        row8 = f"{colored(row8t, 'blue', attrs=['blink'])} {colored(row8t2, 'yellow', attrs=['blink'])}"
        row9t = "           /$$  | $$                                               "
        row9 = f"{colored(row9t, 'blue', attrs=['blink'])} {colored('                         /$$  | $$                    ', 'yellow', attrs=['blink'])}"
        row10t = "          |  $$$$$$/                                               "
        row10t2 = "                        |  $$$$$$/                    "
        row10 = f"{colored(row10t, 'blue', attrs=['blink'])} {colored(row10t2, 'yellow', attrs=['blink'])}"
        row11t = "           \______/                                                "
        row11t2 = "                         \______/                     "
        row11 = f"{colored(row11t, 'blue', attrs=['blink'])} {colored(row11t2, 'yellow', attrs=['blink'])}"
        print(row1)
        print(row2)
        print(row3)
        print(row4)
        print(row5)
        print(row6)
        print(row7)
        print(row8)
        print(row9)
        print(row10)
        print(row11)
        print(f"Made by {colored('python#0001', 'magenta')}")

    def printOptions(self):
        optiontext = colored(self.optiontext, 'green')
        select = f"\n{optiontext}\n\n{colored('Select action : ', 'cyan')}"
        print(select, end="")
        return
    async def console(self, player):
        if self.running is False:
            from termcolor import colored
            query = modules.query.searcher()
            self.running = True
            event = ''
            while True:
                if event != '':
                    def run():
                        os.system('cls')
                        self.intro()
                        print(f"Currently Playing: {player.current}")
                        self.printOptions()
                        return
                    threading.Timer(2.5, run).start()
                event = ''
                optiontext = colored(self.optiontext, 'green')
                select = input(f"\n{optiontext}\n\n{colored('Select action : ', 'cyan')}")
                if select == "a":
                    inp = input(colored("Enter a song query or url: ", 'green'))
                    try:
                        q = await query.querySearch(query=str(inp))
                        event = await player.play(link=q[0], originLink=q[1], trackattrs=q[2])


                    except BaseException as err:
                        event = (colored(f'{err}', 'yellow'))
                elif select == "p":
                    event = await player.pause()
                elif select == "s":
                    event = await player.skip()
                elif select == "q":
                    try:
                        event = await player.viewQueue()
                    except Exception as err:
                        event = (colored(f'{err}', 'yellow'))

                elif select == "v":
                    volume = int(input("Enter an integer for volume: "))
                    event = (await player.volume(volume))

                elif select == "e":
                    choice = input(colored("Are you sure you would like to quit? [Y/n] ", 'red'))
                    print(choice)
                    if choice.lower() == "y":
                        break
                    if not choice:
                        pass
                elif select == "l":
                    if player.current:
                        lyric = lyrics(console=True)
                        lyric.lyric(query=player.current)
                        os.system('mode con: cols=122 lines=19')
                    elif not player.current:
                        event = colored("No current song!", "yellow")


                elif select == "fix":
                    os.system('mode con: cols=122 lines=19')
                os.system('cls')
                self.intro()
                if event != "":
                    print(event)
                else:
                    print(f"Currently Playing: {player.current}")



