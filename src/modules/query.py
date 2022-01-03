import json
import time

from youtubesearchpython import VideosSearch, Playlist
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from yt_dlp import YoutubeDL  # youtube conversion module.
from yt_dlp import extractor
from bs4 import BeautifulSoup
import lxml


def getSpotifyCreds() -> list:
    try:
        with open("creds.json", 'r') as f:
            jsonfile = json.load(f)
            clientid = jsonfile['CLIENT_ID']
            clientsecret = jsonfile['CLIENT_SECRET']
            if clientsecret == "" or clientid == "":
                return ["Missing"]
            return [clientid, clientsecret]
    except:
        return ["Missing"]


class searcher:

    def __init__(self):
        self.current = None
        self.spotifyCreds = getSpotifyCreds

    def serviceChecker(self, arg):
        if ("http" in arg and "://" in arg) or "www." in arg:
            if "youtube." in arg:
                if "list=" in arg:
                    return "YTPlaylist"
                return "Youtube"
            elif "open.spotify." in arg:
                return "Spotify"
            elif "soundcloud." in arg:
                return "Soundcloud"
            elif "music.apple." in arg:
                return "Apple Music"
            else:
                return "Invalid link"
        else:
            if arg == "":
                return "Invalid query"
            return "Youtube query"

    def formatter(self, formatObject):
        querystring = formatObject

        def rem_par(qs):
            ret = ''
            skip1c = 0
            skip2c = 0
            for i in qs:
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

        querystring = rem_par(querystring)
        querystring = str(querystring).lower().replace("lyrics", "")
        querystring = str(querystring).lower().replace("music video", "")
        querystring = str(querystring).lower().replace("official audio", "")
        querystring = str(querystring).lower().replace("official video", "")
        querystring = str(querystring).lower().replace("audio", "")
        finalString = ""
        for i in range(0, len(querystring)):
            if querystring[i] == formatObject[i].lower():
                finalString = finalString + formatObject[i]
        return finalString

    async def ytPlaylistSearch(self, query, player=None):
        playlistSearch = Playlist(query)
        origin0 = playlistSearch.videos[0]
        done = False
        index = 0
        while not done:
            try:
                if playlistSearch.videos[index] == origin0:
                    res = await self.querySearch(f"https://www.youtube.com/watch?v={playlistSearch.videos[0]['id']}")
                    await player.play(link=res[0], originLink=res[1], trackattrs=res[2])
                else:
                    await player.play(link="No link", originLink=f"https://www.youtube.com/watch?v={playlistSearch.videos[index]['id']}", trackattrs=playlistSearch.videos[index]['title'])
                index = index + 1
                if index == 100 and playlistSearch.hasMoreVideos:
                    playlistSearch.getMoreVideos()
                    index = 0
                elif not index == 100:
                    continue
                else:
                    done = True
            except:
                done = True



    async def youtubeSearch(self, query, list=False):
        videosSearch = VideosSearch(f"{self.formatter(query)} audio", limit=1)
        try:
            title = self.formatter(videosSearch.result()['result'][0]['title'])
            link = videosSearch.result()['result'][0]['link']
            if list:
                return [link, title]
            else:
                return link
        except:
            return "no results"

    async def spotifyConverter(self, trackURL, player=None):
        creds = self.spotifyCreds()
        if creds[0] == "Missing":
            raise Exception("Please enter your spotify API credentials in the 'creds.json' file.")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=creds[0],
            client_secret=creds[1]
        )
        if "/track/" in trackURL:

            spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            PreID, IDwithcode = trackURL.split("/track/")
            try:
                final, recycle = IDwithcode.split("?")
            except:
                final = IDwithcode

            name = spotify.track(track_id=final)['name']
            art = spotify.track(track_id=final)['artists'][0]['name']
            query = f'{name} {art} audio'
            return await self.youtubeSearch(query)
        elif "/playlist/" in trackURL:
            spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            results = spotify.user_playlist_tracks(user="", playlist_id=trackURL)
            tracks = []
            for i, item in enumerate(results['items']):
                track = item['track']
                artist = track["artists"][0]["name"]
                name = track["name"]
                query = f"{artist} {name}"
                tracks.append(query)

            res = await self.querySearch(await self.youtubeSearch(tracks[0]))
            await player.play(link=res[0], originLink=res[1], trackattrs=res[2])
            for track in tracks:
                if track is tracks[0]:
                    continue
                trackattrs = await self.youtubeSearch(track, list=True)
                await player.play(link="No link", trackattrs=trackattrs[1], originLink=trackattrs[0])
            return ["playlist"]
        elif "/album/" in trackURL:
                PreID, IDwithcode = trackURL.split("/album/")
                try:
                    final, recycle = IDwithcode.split("?")
                except:
                    final = IDwithcode

                AUTH_URL = 'https://accounts.spotify.com/api/token'
                resp = requests.post(AUTH_URL, {
                    'grant_type': 'client_credentials',
                    'client_id': creds[0],
                    'client_secret': creds[1],
                })
                jsonfile = resp.json()
                token = jsonfile["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                request = requests.get(url=f"https://api.spotify.com/v1/albums/{final}/tracks",
                                       headers=headers)
                results = request.json()
                tracks = []
                for i, item in enumerate(results['items']):
                    track = item['track']
                    artist = track["artists"][0]["name"]
                    name = track["name"]
                    query = f"{artist} {name}"
                    tracks.append(query)
                print("indexing first track")
                res = await self.querySearch(await self.youtubeSearch(tracks[0]))
                await player.play(link=res[0], originLink=res[1], trackattrs=res[2])
                for track in tracks:
                    if track is tracks[0]:
                        continue
                    trackattrs = await self.youtubeSearch(track, list=True)
                    await player.play(link="No link", trackattrs=trackattrs[1], originLink=trackattrs[0])
                return ["playlist"]



    async def querySearch(self, query, playlist=False, player=None):
        # Player is only provided if needed to loop queue from inside the function (playlists.)
        service = self.serviceChecker(query)

        if service == "Invalid query":
            raise Exception("That query is invalid!")

        if service == "Invalid link":
            raise Exception("This URL is not supported by our player!")
        else:
            if service == "Youtube query":
                link = await self.youtubeSearch(f"{query}", list=playlist)
                if link == "no results":
                    raise Exception(f"No results found for: \"{query}\"!")
                if playlist:
                    return link
                youtube_dl_opts = {'quiet': True}
                with YoutubeDL(youtube_dl_opts) as ydl:
                    info_dict = ydl.extract_info(link, download=False)
                    for entry in info_dict['formats']:
                        if entry['url'] is not None:
                            if "audio" in entry['url'] and not "mp4" in entry['url']:
                                return [entry['url'], link, self.formatter(info_dict['title'])]
                            else:
                                pass
                        else:
                            pass

            else:
                if service == "YTPlaylist":
                    if "&list=" in query:
                        query = query.split("&list=")
                        query = "https://www.youtube.com/playlist?list=" + query[1]
                        await self.ytPlaylistSearch(query, player)
                    else:
                        await self.ytPlaylistSearch(query, player)

                if service == "Soundcloud":
                    youtube_dl_opts = {'quiet': True}
                    with YoutubeDL(youtube_dl_opts) as ydl:
                        info_dict = ydl.extract_info(query, download=False)
                        for entry in info_dict['formats']:
                            if entry['url'] is not None:
                                if ".mp3?Pol" in entry['url']:  # avoid getting the m3u8 link instead of the mp3.
                                    return [entry['url'], query, self.formatter(info_dict['title'])]
                if service == "Spotify":
                    link = await self.spotifyConverter(query, player=player)
                    youtube_dl_opts = {'quiet': True}
                    with YoutubeDL(youtube_dl_opts) as ydl:
                        info_dict = ydl.extract_info(link, download=False)
                        return [info_dict['formats'][0]['url'], query, self.formatter(info_dict['title'])]

                if service == "Youtube":
                    youtube_dl_opts = {'quiet': True}
                    with YoutubeDL(youtube_dl_opts) as ydl:
                        info_dict = ydl.extract_info(query, download=False)
                        for entry in info_dict['formats']:
                            if entry['url'] is not None:
                                if "audio" in entry[
                                    'url']:  # avoid playing the video version or a secondary window will pop up with the video.
                                    return [entry['url'], query, self.formatter(info_dict['title'])]
                                else:
                                    pass
                            else:
                                pass
                if service == "Apple Music":
                    if "/playlist/" in query:
                        headers = {
                            'User-Agent':
                                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
                        }
                        url = query
                        splitted = str(url).split('/')
                        splitted = splitted[:3] + ['us'] + splitted[4:]
                        url = '/'.join(splitted)

                        response = requests.get(url, headers=headers)
                        soup = BeautifulSoup(response.text, 'lxml')

                        data, name, artist = None, None, None
                        tracks = []
                        removed = False

                        for link in soup.findAll('meta', attrs={'property': 'music:song_count'}):
                            data = link.get('content')
                            if int(data):
                                for link in soup.findAll('meta', attrs={'property': 'music:song'}):
                                    data = link.get('content')
                                    splits = str(data).split('/')
                                    name = str(splits[5])
                                    name = name.replace('-', ' ')
                                    tracks.append(name)
                                    pass

                                break
                        artists = []

                        for link in soup.findAll("div", attrs={"class": "songs-list-row__by-line"}):
                            tmpstr = ""

                            for link in link.findAll("a", attrs={"class": "songs-list-row__link"}):
                                split = str(link).split("href=\"")
                                split = split[1].split("\"")
                                url = split[0]
                                if "artist" in url:
                                    urlsplit = url.split("/")
                                    fin = urlsplit[5].replace("-", " ")
                                    tmpstr = tmpstr + fin + " "
                                    continue
                                else:
                                    pass
                            artists.append(tmpstr)
                            tmpstr = ""
                        finalTracks = []
                        for entry in tracks:
                            finalTracks.append(f"{entry} {artists[tracks.index(entry)]}")
                        res = await self.querySearch(await self.youtubeSearch(finalTracks[0]))
                        await player.play(link=res[0], originLink=res[1], trackattrs=res[2])
                        for track in finalTracks:
                            if track is finalTracks[0]:
                                continue
                            trackattrs = await self.youtubeSearch(track, list=True)
                            await player.play(link="No link", trackattrs=trackattrs[1], originLink=trackattrs[0])
                        return ["playlist"]

                    elif "/album/" in query:
                        headers = {
                            'User-Agent':
                                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
                        }

                        url = query

                        splitted = str(url).split('/')
                        splitted = splitted[:3] + ['us'] + splitted[4:]
                        url = '/'.join(splitted)
                        response = requests.get(url, headers=headers)
                        soup = BeautifulSoup(response.text, 'lxml')
                        data, name, artist = None, None, None

                        for link in soup.findAll('meta', attrs={'property': 'og:title'}):
                            data = link.get('content')
                            splitlist = str(data).split("on Apple")
                            splitlist2 = splitlist[0].split(' by')
                            artist = splitlist2[1]
                            break
                        tracks = []

                        for link in soup.findAll('meta', attrs={'property': 'music:song'}):
                            data = link.get('content')
                            splits = str(data).split('/')
                            name = str(splits[5])
                            name = name.replace('-', ' ')
                            final = f"{name} {artist}"
                            tracks.append(final)

                        res = await self.querySearch(await self.youtubeSearch(tracks[0]))
                        await player.play(link=res[0], originLink=res[1], trackattrs=res[2])
                        for track in tracks:
                            if track is tracks[0]:
                                continue
                            trackattrs = await self.youtubeSearch(track, list=True)
                            await player.play(link="No link", trackattrs=trackattrs[1], originLink=trackattrs[0])

                        return ["playlist"]

