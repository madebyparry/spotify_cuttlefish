#!/usr/bin/env python3
# import sys,os
import curses
import cuttlefish
import time
import catimage


catimg = catimage


def draw_menu(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    # stdscr.clear()
    # stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while True:
        # Initialization
        # stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            cuttlefish.playPauseMusic()
        elif k == curses.KEY_UP:
            cuttlefish.like_song()
        elif k == curses.KEY_SRIGHT:
            cuttlefish.nextTrack()
        elif k == curses.KEY_SLEFT:
            cuttlefish.prevTrack()

        if k == ord("q"):
            break

        cursor_x = max(0, cursor_x)
        cursor_x = min(width - 1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height - 1, cursor_y)

        # get spotify values
        current_runtime = cuttlefish.printCurrentRuntime()
        if "currently_playing" in locals():
            stored_track = currently_playing["track_name"]
        else:
            stored_track = ""
        currently_playing = cuttlefish.currentlyPlaying()

        def get_track_data():
            td = {}
            td["data"] = currently_playing

        #        song_duration = {
        #                'minutes_elapsed' : ,
        #                'seconds_elapsed' : ,
        #                'minutes_remaining' : ,
        #                'seconds_remaining' : ,
        #                }
        #        song_info = {
        #                'artist_name' : ,
        #                'song_name' : ,
        #                'album_art' : ,
        #                'album_name' : ,
        #                }
        # Declaration of strings
        # keystr = "Spotify Cuttlefish Player"[: width - 1]
        # track_status = ">"
        # subtitle = "{}".format(currently_playing["album_name"])[: width - 1]
        # title = "{} - {}".format(
        #     currently_playing["track_name"], currently_playing["artist_name"]
        # )[: width - 1]
        # statusbarstr = " {} | CUTTLEFISH | {}".format(track_status, current_runtime)
        # album_art = currently_playing["album_art"]

        # Centering calculations
        # start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        # start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        # start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)
        start_album_art_x = 2
        start_album_art_y = 2

        # make windows
        album_win_width = (height - 4) * 2
        album_window = curses.newwin(
            (height - 4), album_win_width, start_album_art_y, start_album_art_x
        )

        # info_window = curses.newwin(8, round(width / 2))
        # album_window = curses.newpad(50, 50) #, start_album_art_y, start_album_art_x)
        # album_window.border()
        # playing_window = curses.newwin()
        def print_album_art():
            rendered_album_art = cuttlefish.displayCatImg(
                currently_playing["album_art"], 10
            )
            rendered_album_art = catimage.generateGreyscale(
                "/home/nicholas/spotify_cuttlefish/data/album_art_cache",
                (round(height * 2) - 9),
            )
            album_window.addstr(rendered_album_art)

        # Rendering some text
        # whstr = "Width: {}, Height: {} {}".format(width, height, stored_track)
        # stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        # win = curses.newwin(height, width, begin_y, begin_x)
        status_win = curses.newwin(1, width, height - 1, 0)

        def render_status_bar():
            track_status = ">"
            statusbarstr = " {} | CUTTLEFISH | {}".format(track_status, current_runtime)
            # status_win = curses.newwin(1, width, height - 1, 0)
            status_win.attron(curses.color_pair(3))
            status_win.addstr(0, 0, statusbarstr)
            status_win.addstr(
                0, len(statusbarstr), " " * (width - len(statusbarstr) - 1)
            )
            status_win.attroff(curses.color_pair(3))

        text_window = curses.newwin(
            height - 2, width - album_win_width, 1, album_win_width
        )

        def render_text():
            subtitle = "{}".format(currently_playing["album_name"])[: width - 1]
            title = "{} - {}".format(
                currently_playing["track_name"], currently_playing["artist_name"]
            )[: width - 1]

            # Turning on attributes for title
            text_window.attron(curses.color_pair(2))
            text_window.attron(curses.A_BOLD)

            # Rendering song title
            text_window.addstr(3, 2, title)

            # Turning off attributes for title
            text_window.attroff(curses.color_pair(2))
            text_window.attroff(curses.A_BOLD)

            # Print rest of text
            text_window.addstr(1, 2, subtitle)  # todo change that stupid as fuck name
            text_window.addstr(2, 2, "-" * len(subtitle))
            # text_window.addstr(start_y + 5, (height * 2), keystr)

        stdscr.move(cursor_y, cursor_x)
        stdscr.nodelay(True)
        # Refresh the screen
        time.sleep(1)
        k = stdscr.getch()
        render_status_bar()
        status_win.refresh()
        # stdscr.refresh()
        if stored_track != currently_playing["track_name"]:
            stdscr.clear()
            stdscr.refresh()
            text_window.clear()
            render_text()
            text_window.refresh()
            album_window.clear()
            print_album_art()
            album_window.refresh()
            # album_window.refresh(0,0,2,2,50,50)
        elif stored_track == "":
            stdscr.clear()
            stdscr.refresh()
            text_window.clear()
            render_text()
            text_window.refresh()
            album_window.clear()
            print_album_art()
            album_window.refresh()
        # stdscr.getch()
        # Wait for next input


def main():
    cuttlefish.setEnvVars()
    # cuttlefish.authenticateSpotipyOauth()
    # cuttlefish.authenticateSpotipyCreds()
    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()
