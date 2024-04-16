#!/usr/bin/env python3

import spotipy
import player
import sys
import subprocess
import os
import inquirer
import cf_bc
from cf_wiki import wikiSectionsGenerate, wikiSummary, getWikiSelection
from random import randint
from time import sleep
from dotenv import load_dotenv, dotenv_values
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


def main():
    setEnvVars()
    userSelect = inquirer_initialize("Cuttlefish options: ", initial_choices)
    triageSelection(userSelect)


# ----------------------------------------------------
# Set up environment variables and spotipy
# ----------------------------------------------------


def setEnvVars():
    global sp
    global sessionUser
    global SPOTIPY_CLIENT_ID
    global SPOTIPY_CLIENT_SECRET
    global SPOTIPY_REDIRECT_URI
    global sp_oauth
    sys_user_home = os.path.expanduser("~")
    dir_path = sys_user_home + "/spotify_cuttlefish/cuttlefish"
    env_file = dir_path[:-11] + "/data/.env"
    auth_cache = dir_path[:-11] + "/data/.cache"
    # TODO: make session username dynamic... Based on oauth2 token likely...
    sessionUser = "73e213ujw0wxcy49bxwcfuhik"
    try:
        load_dotenv(env_file)
        env_vals = dotenv_values(env_file)
        SPOTIPY_CLIENT_ID = env_vals["SPOTIPY_CLIENT_ID"]
        SPOTIPY_CLIENT_SECRET = env_vals["SPOTIPY_CLIENT_SECRET"]
        SPOTIPY_REDIRECT_URI = env_vals["SPOTIPY_REDIRECT_URI"]
    except:
        print("Spotipy says: data/.env data not set ;-(")
    # access_token = ''
    scope = "user-read-playback-state,playlist-modify-private,user-library-modify,user-modify-playback-state,user-read-currently-playing,user-top-read,streaming,playlist-read-private,user-follow-modify,user-read-recently-played,user-library-read"
    sp_oauth = oauth2.SpotifyOAuth(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope
    )
    token_cache = sp_oauth.get_cached_token()
    if not token_cache:
        print("set env vars")
    # if access_token:
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            SPOTIPY_CLIENT_ID,
            SPOTIPY_CLIENT_SECRET,
            SPOTIPY_REDIRECT_URI,
            scope=scope,
            cache_path=auth_cache,
            username=sessionUser,
            open_browser=False,
        )
    )
    sp.devices()
    # else:
    # authenticateSpotipyOauth()
    # run(host='localhost', port=9088)


# ----------------------------------------------------
# Spotipy authentication methods:
# ----------------------------------------------------


def authenticateSpotipyCreds():
    global sp
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)


def authenticateSpotipyOauth():
    auth_url = sp_oauth.get_authorize_url()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


# ----------------------------------------------------
# Convenience functions
# ----------------------------------------------------


def inquirer_initialize(user_message: str, user_list):
    inquirer_list = [
        inquirer.List(
            "inquirer_result",
            message=user_message,
            choices=user_list,
        ),
    ]
    user_selection = inquirer.prompt(inquirer_list)
    return user_selection["inquirer_result"]


# ----------------------------------------------------
# Basic API functionality
# ----------------------------------------------------


def listUserPlaylists():
    print("list playlists")
    # authenticateSpotipyCreds()
    playlists = sp.user_playlists(sessionUser)
    while playlists:
        for i, playlist in enumerate(playlists["items"]):
            print(
                "%4d %s %s"
                % (i + 1 + playlists["offset"], playlist["uri"], playlist["name"])
            )
        if playlists["next"]:
            playlists = sp.next(playlists)
        else:
            playlists = None


def userTopArtists(ranges=["short_term", "medium_term", "long_term"]):
    top_artists = []
    results = sp.current_user_top_artists(time_range=ranges, limit=50)
    for i, item in enumerate(results["items"]):
        top_artists.append(item["name"])
    return top_artists


def printUserTopArtists():
    ranges = ["short_term", "medium_term", "long_term"]
    print("Your top artists:")
    for i in ranges:
        top_artists = userTopArtists(i)
        print("\n-----------------")
        print("Range: " + i)
        print("-----------------\n")
        c = 1
        for i in top_artists:
            print("\t", str(c) + ":", i)
            c += 1
        print()
    print()


def searchRelated():
    print("related artists")
    artist_name = input("Related to whom? >> ")
    authenticateSpotipyCreds()
    result = sp.search(q="artist:" + artist_name, type="artist")
    try:
        name = result["artists"]["items"][0]["name"]
        uri = result["artists"]["items"][0]["uri"]

        related = sp.artist_related_artists(uri)
        print("Related artists for", name)
        for artist in related["artists"]:
            print("  ", artist["name"])
    except BaseException:
        print("No related artists: " + artist_name)


def relatedArtists():
    playing = currentlyPlaying()
    artist_name = playing["artist_name"]
    authenticateSpotipyCreds()
    result = sp.search(q="artist:" + artist_name, type="artist")
    try:
        name = result["artists"]["items"][0]["name"]
        uri = result["artists"]["items"][0]["uri"]

        related = sp.artist_related_artists(uri)
        print("Related artists for", name)
        print()
        for artist in related["artists"]:
            print("  ", artist["name"])
        print("\n-----------------------------\n")
        sleep(1)
    except:
        print("No related artists: " + artist_name)
        print()


def searchArtistRecommendation():
    print('Note: Enter "no" for random')
    user_in = input("Any starting artist for the recommendations? >> ")
    if user_in == "no" or user_in == "":
        tops = userTopArtists(["short_term"])
        return tops[randint(0, len(tops) - 1)]
    else:
        return user_in


def recommendFromArtist(artist_name):
    results = sp.search(q="artist:" + artist_name, type="artist")
    items = results["artists"]["items"]
    print("We'll try to find some recs for " + artist_name)
    authenticateSpotipyCreds()
    if len(items) > 0:
        results = sp.recommendations(seed_artists=[items[0]["id"]])
        c = 0
        rec_list = []
        rec_ids = []
        for track in results["tracks"]:
            rec_line = (
                str(c) + ": " + track["name"] + " - " + track["artists"][0]["name"]
            )
            rec_id = track["id"]
            print(rec_line)
            rec_list.append(rec_line)
            rec_ids.append(rec_id)
            c += 1
        rec_list.append("-----------------")
        saveThemRecs(rec_list)
        track_selection = inquirer_initialize("play a song? ", rec_list)
        start_track(track_selection)
    else:
        print("Seems like there is no recommendations found for " + artist_name)
        print()


def saveThemRecs(recs):
    data_root = os.path.expanduser("~") + "/spotify_cuttlefish/data/"
    recs_file = data_root + "recommendations.txt"
    with open(recs_file, "a") as f:
        try:
            for i in recs:
                f.write("%s\n" % i)
        except:
            print("Recommendations file is not found: ")
            print(recs_file)


def currentRuntime():
    track = sp.current_user_playing_track()

    def readableTime(ms):
        time = []
        x = ms / 1000
        seconds = x % 60
        x /= 60
        minutes = x % 60
        time.append(seconds)
        time.append(minutes)
        return time

    if not track is None:
        times = {}
        progress = readableTime(track["progress_ms"])
        duration = readableTime(track["item"]["duration_ms"])
        times["progress_seconds"] = round(progress[0])
        times["progress_minutes"] = round(progress[1])
        times["duration_seconds"] = round(duration[0])
        times["duration_minutes"] = round(duration[1])
        times["progress_ms"] = track["progress_ms"]
        times["duration_ms"] = track["item"]["duration_ms"]
        return times
    else:
        return "No track currently playing."


def sanitizeNamesUTF(input):
    output = input.encode("utf-8", errors="ignore").decode("utf-8")
    return output


def printCurrentRuntime():
    track_time = currentRuntime()
    running_time_sec = str(track_time["progress_seconds"])
    running_time_min = str(track_time["progress_minutes"])
    total_time_sec = str(track_time["duration_seconds"])
    total_time_min = str(track_time["duration_minutes"])
    if len(total_time_sec) < 2:
        total_time_sec = "0" + total_time_sec
    if len(running_time_sec) < 2:
        running_time_sec = "0" + running_time_sec
    pretty_print_time = (
        running_time_min
        + ":"
        + running_time_sec
        + "/"
        + total_time_min
        + ":"
        + total_time_sec
    )
    return pretty_print_time


def currentlyPlaying():
    def check_if_track():
        err = 0
        track = sp.current_user_playing_track()
        while not track:
            print("no track detected, reauthorizing...")
            err = err + 1
            print("reconnecting... " + str(err))
            setEnvVars()
            authenticateSpotipyOauth()
            sleep(5)
            track = sp.current_user_playing_track()
        return True

    track_status = check_if_track()
    if track_status:
        track = sp.current_user_playing_track()
        playing = {}
        playing["track_id"] = track["item"]["id"]
        playing["album_id"] = track["item"]["album"]["id"]
        playing["artist_id"] = track["item"]["artists"][0]["id"]
        playing["track_url"] = track["item"]["external_urls"]["spotify"]
        playing["album_art"] = track["item"]["album"]["images"][0]["url"]
        playing["track_name"] = sanitizeNamesUTF(track["item"]["name"])
        playing["artist_name"] = sanitizeNamesUTF(track["item"]["artists"][0]["name"])
        playing["album_name"] = sanitizeNamesUTF(track["item"]["album"]["name"])
        playing["feat_artist"] = []
        if len(track["item"]["artists"]) > 1:
            for i in track["item"]["artists"][1:]:
                playing["feat_artist"].append(sanitizeNamesUTF(i["name"]))
                playing["feat_artist_id"] = i["id"]
        return playing
    else:
        print(
            "problem loading track... try checking your system is operational and spotify is active."
        )
        main()


def printCurrentlyPlaying():
    playing = currentlyPlaying()
    if len(playing) > 0:
        runtime = printCurrentRuntime()
        album_size = 80
        print(displayCatImg(playing["album_art"], album_size))
        print(playing["artist_name"] + " - " + playing["album_name"])
        print(playing["track_name"])
        print(runtime)
        sleep(2)
    else:
        print("| ----------------------------------")
        print("| Error:")
        print("| No track currently playing.")
        print("| ----------------------------------\n")
        sleep(1)


def displayCatImg(album_art, album_size):
    os.system("wget -q " + album_art)
    os.system("mv " + album_art[24:] + " data/album_art_cache")
    # os.system('catimg -w ' + str(album_size) + ' data/album_art_cache')
    return subprocess.run(
        ["catimg", "-w", str(album_size), "data/album_art_cache"], capture_output=True
    ).stdout.decode()


def printPretty(print_input, prepend=""):
    c = 0
    print(prepend, end="")
    for i in print_input:
        if c > 100 and i == " ":
            print(i)
            print(prepend, end="")
            c = 0
        elif i == "\n":
            print(i, end="")
            print(prepend, end="")
            c = 0
        else:
            print(i, end="")
            c += 1
    print("\n")


# ----------------------------------------------------
# Wiki printing
# ----------------------------------------------------


def wikiSectionSelector(artist_wiki):
    # Generate inquirer list for sections
    section_selections = wikiSectionsGenerate(artist_wiki)
    return_tuple = ("-- RETURN --", 99)
    section_selections.append(return_tuple)
    sectionSelected = inquirer_initialize(
        "More about " + artist_wiki.title + " :", section_selections
    )

    def printSectionsNested(sections):
        for i in sections:
            print("------- " + i.title + " -------")
            printPretty(i.text, "\t")
            printSectionsNested(i.sections)

    if sectionSelected == 99:
        return
    else:
        value = sectionSelected
        key = section_selections[value][0]
        printSectionsNested(artist_wiki.sections_by_title(key))
        wikiSectionSelector(artist_wiki)


def validateWiki(override=""):
    playing = currentlyPlaying()
    if override:
        selected_artist = override
    elif playing["feat_artist"]:
        selected_artist = selectArtist(playing)
    else:
        selected_artist = playing["artist_name"]
    artist_wiki = getWikiSelection(selected_artist)
    valid_categories_term = "music"
    valid_artist_wiki = False
    if artist_wiki:
        if not artist_wiki.categories:
            print("page exists but does not have cateories?")
            print(artist_wiki)
            artist_wiki == False
        for i in artist_wiki.categories:
            if valid_categories_term in i:
                valid_artist_wiki = True
        if valid_artist_wiki == False:
            print("categories do not seem like a valid musician")
            for i in artist_wiki.links:
                if "(band)" in i:
                    print("trying again with " + i)
                    validateWiki(i)
                else:
                    artist_wiki = None
        if valid_artist_wiki:
            print("------- " + artist_wiki.title + " -------")
            printPretty(wikiSummary(artist_wiki), "\t")
            print("-------------------------------------------------\n")
            wikiSectionSelector(artist_wiki)
    else:
        print("| ----------------------------------")
        print("| Error:")
        print("| No wikipedia page found for that search. ")
        print("| ----------------------------------\n")
        sleep(1)


# ----------------------------------------------------
# Bandcamp functionality
# ----------------------------------------------------


def validateBandcamp():
    playing = currentlyPlaying()
    search_result = cf_bc.search_artist(playing["artist_name"])
    print(search_result.artist_title + " found")
    print("url: " + search_result.url)
    # for i in search_result.album_urls:
    #    print('\t' + i)


def selectArtist(playing):
    if playing["feat_artist"]:
        feat_artists = [playing["artist_name"]]
        for i in playing["feat_artist"]:
            feat_artists.append(i)
        selected_artist = inquirer_initialize(
            "Multiple artists on this track: ", feat_artists
        )
        print(selected_artist)
        return selected_artist


# ----------------------------------------------------
# Basic playback
# ----------------------------------------------------


def start_track(track_id: list):
    sp.start_playback(uris=track_id)


def playPauseMusic():
    track = sp.currently_playing()
    if track["is_playing"] is False:
        sp.start_playback()
    else:
        sp.pause_playback()


def nextTrack():
    sp.next_track()


def prevTrack():
    sp.previous_track()


def volumeControl():
    sp.volume(99)
    sleep(2)
    sp.volume(50)
    sleep(2)
    sp.volume(99)


def get_liked_songs(max_songs=50):
    liked_songs = []
    liked_songs_raw = sp.current_user_saved_tracks(limit=max_songs)
    for song_data in liked_songs_raw["items"]:
        song = {}
        song["track_name"] = song_data["track"]["name"]
        song["track_id"] = song_data["track"]["id"]
        song["artist_name"] = song_data["track"]["artists"][0]["name"]
        liked_songs.append(song)
    return liked_songs


def clear_queue():
    print("queue cleared!")


def queue_track_from_selection(selection):
    selection_list = []
    for i in selection:
        selection_list.append(i["track_name"] + " - " + i["artist_name"])
    user_select = inquirer_initialize("Which track? ", selection_list)
    indexof_selection = selection_list.index(user_select)
    sp.add_to_queue(selection[indexof_selection]["track_id"])


def get_current_album_id():
    playing = currentlyPlaying()
    return playing["album_id"]


def get_tracks_from_album_id(album_id):
    album_tracks_raw = sp.album_tracks(album_id, limit=50)
    album_tracks = []
    for song in album_tracks_raw["items"]:
        album_tracks.append(song)
        print(song["name"])
    return album_tracks


def play_album(album):
    my_devices = sp.devices()
    on_device = my_devices["devices"][0]["id"]
    print(my_devices)
    print(get_tracks_from_album_id(album))
    sp.start_playback(device_id=on_device, context_uri=album)


def add_songs_to_queue(tracks: list):
    for track in tracks:
        if track["name"]:
            sp.add_to_queue(track["id"])


def like_song():
    playing = currentlyPlaying()
    track_list = []
    track_list.append(playing["track_id"])
    sp.current_user_saved_tracks_add(track_list)
    return playing["track_name"], playing["artist_name"]
    # print(
    #     "Liked song: " + playing["track_name"] + " - " + playing["artist_name"] + "\n"
    # )


def print_liked_song(track_name, artist_name):
    print("Liked song: " + track_name + " - " + artist_name + "\n")


def print_dev():
    print(sp.devices())


def triageSelection(user_choice):
    if user_choice == "related artists":
        relatedArtists()
        main()
    elif user_choice == "search related":
        searchRelated()
        main()
    elif user_choice == "recommendations":
        recommendFromArtist(searchArtistRecommendation())
        main()
    elif user_choice == "user top artists":
        printUserTopArtists()
        main()
    elif user_choice == "user playlists":
        listUserPlaylists()
        main()
    elif user_choice == "currently playing":
        printCurrentlyPlaying()
        main()
    elif user_choice == "play/pause music":
        playPauseMusic()
        main()
    elif user_choice == "next track":
        nextTrack()
        printCurrentlyPlaying()
        main()
    elif user_choice == "current runtime":
        print(printCurrentRuntime())
        main()
    elif user_choice == "check wiki":
        validateWiki()
        main()
    elif user_choice == "check bandcamp":
        validateBandcamp()
        main()
    elif user_choice == "liked songs":
        get_liked_songs()
        main()
    elif user_choice == "clear queue":
        clear_queue()
        main()
    elif user_choice == "queue this album":
        add_songs_to_queue(get_tracks_from_album_id(get_current_album_id()))
        main()
    elif user_choice == "queue a liked song":
        queue_track_from_selection(get_liked_songs())
        main()
    elif user_choice == "like song":
        track, artist = like_song()
        print_liked_song(track, artist)
        main()
    elif user_choice == "volume":
        volumeControl()
        main()
    elif user_choice == "dev":
        print_dev()
        main()
    elif user_choice == "player app":
        player.main()
    elif user_choice == "shutdown":
        print("Bye-bye!")
        return
    else:
        print(user_choice)
        print("Bye-bye!")
        return


initial_choices = [
    "currently playing",
    "like song",
    "check wiki",
    "check bandcamp",
    "current runtime",
    "play/pause music",
    "next track",
    "recommendations",
    "related artists",
    "search related",
    "user top artists",
    "user playlists",
    "liked songs",
    "queue this album",
    "queue a liked song",
    "clear queue",
    "volume",
    "dev",
    "player app",
    "shutdown",
]


if __name__ == "__main__":
    main()
