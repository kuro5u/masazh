#!/usr/bin/env python3

import subprocess
import argparse
import requests
import signal
import json
import sys
import re
import utils
from colorama import Fore
from unidecode import unidecode

def banner():
    print(Fore.GREEN)
    print(" ███▄ ▄███▓ ▄▄▄        ██████  ██░ ██  ▄▄▄      ▒███████▒")
    print("▓██▒▀█▀ ██▒▒████▄    ▒██    ▒ ▓██░ ██▒▒████▄    ▒ ▒ ▒ ▄▀░")
    print("▓██    ▓██░▒██  ▀█▄  ░ ▓██▄   ▒██▀▀██░▒██  ▀█▄  ░ ▒ ▄▀▒░ ")
    print("▒██    ▒██ ░██▄▄▄▄██   ▒   ██▒░▓█ ░██ ░██▄▄▄▄██   ▄▀▒   ░")
    print("▒██▒   ░██▒ ▓█   ▓██▒▒██████▒▒░▓█▒░██▓ ▓█   ▓██▒▒███████▒")
    print("░ ▒░   ░  ░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒ ▒▒   ▓▒█░░▒▒ ▓░▒░▒")
    print("░  ░      ░  ▒   ▒▒ ░░ ░▒  ░ ░ ▒ ░▒░ ░  ▒   ▒▒ ░░░▒ ▒ ░ ▒")
    print("░      ░     ░   ▒   ░  ░  ░   ░  ░░ ░  ░   ▒   ░ ░ ░ ░ ░")
    print("       ░         ░  ░      ░   ░  ░  ░      ░  ░  ░ ░    ")
    print("                                                ░        ")
    print(Fore.RESET)

def find_active_sink():
    command = ['/usr/bin/pactl', 'list', 'sinks', 'short']
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    for line in result.stdout.splitlines():
        if 'RUNNING' in line:
            sink = line.split('\t')[1]
            return sink
    return None

def recognize_song_from_sink(sink):
    thread = utils.BackgroundTasks()
    thread.start()
    command = ['/usr/bin/songrec', 'recognize', '-d', f'{sink}.monitor', '-j']
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def parse_songrec_results(song_data):
    json_data = json.loads(song_data)
    artist = json_data['track']['subtitle']
    song = json_data['track']['title']
    metadata = json_data['track']['sections'][0]['metadata']
    album = metadata[0]['text'] if metadata else '-'
    year = metadata[2]['text'] if metadata else '-'
    label = metadata[1]['text'] if metadata else '-'
    return artist, song, album, year, label

def find_lyrics(artist, song):
    artist = ''.join(artist)
    artist = unidecode(artist)
    artist = re.sub(r'[^A-Za-z]+', '', artist)
    artist = artist.lower().strip()

    song = ''.join(song)
    song = unidecode(song)
    song = re.sub(r' \(.*?\)', '', song)
    song = re.sub(r'[^A-Za-z]+', '', song)
    song = song.lower().strip()

    url = f"https://www.azlyrics.com/lyrics/{artist}/{song}.html"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    result = requests.get(url, headers={'User-Agent': user_agent})

    if result.status_code != 200:
        return

    html = result.text

    artist = re.findall(r'artist: "(.*?)"', html, re.DOTALL)[0]
    song = re.findall(r'song: "(.*?)"', html, re.DOTALL)[0]

    lyrics = re.findall(r'<div>(.*?)</div>', html, re.DOTALL)[0]
    lyrics = re.sub(r'<br>', '', lyrics)
    lyrics = re.sub(r'<i>', '', lyrics)
    lyrics = re.sub(r'<!.*-->', '', lyrics)
    lyrics = re.sub(r'&quot;', '"', lyrics)
    lyrics = lyrics[2:]

    return lyrics

def pretty_print(artist, song, album, year, label, lyrics=None):
    utils.clear_message()
    print(f"{Fore.BLUE}Artist: {Fore.RESET}{artist}")
    print(f"{Fore.BLUE}Song: {Fore.RESET}{song}")
    print(f"{Fore.BLUE}Album: {Fore.RESET}{album}")
    print(f"{Fore.BLUE}Year: {Fore.RESET}{year}")
    print(f"{Fore.BLUE}Label: {Fore.RESET}{label}")
    print()
    if lyrics:
        print(f"\t{Fore.BLUE}[ Lyrics ]{Fore.RESET}\n{lyrics}")

if __name__ == "__main__":

    signal.signal(signal.SIGINT, utils.handle_sigint)

    parser = argparse.ArgumentParser(description="Mashaz - Get information for the song currently playing on your device")
    # parser.add_argument('-a', nargs='+', help='Artist name')
    # parser.add_argument('-s', nargs='+', help='Song name')
    parser.add_argument('-l', action='store_true', help='Get song lyrics')
    args = parser.parse_args()

    banner()

    sink = find_active_sink()
    if not sink:
        print("Error: Couldn't identify active sink")
        sys.exit(1)

    song_metadata = recognize_song_from_sink(sink)

    artist, song, album, year, label = parse_songrec_results(song_metadata)

    if args.l:
        lyrics = find_lyrics(artist, song)
        pretty_print(artist, song, album, year, label, lyrics)
    else:
        pretty_print(artist, song, album, year, label)
