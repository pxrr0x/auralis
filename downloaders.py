"""
Auralis - Command-Line Music & Playlist Downloader
CS50x Final Project - Harvard University

Author: Prince Addai Desmond | pxrr0x
Date: 30th May 2026
"""

import os
import sys
import re
import requests
import syncedlyrics
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, USLT
from ytmusicapi import YTMusic

# Init YT Music
yt = YTMusic()

APP_NAME = "auralis"
PROJECT_NAME = "Aurora"
VERSION = "0.0.1"
home_dir = os.path.expanduser("~")


def check_system():
    """
    Detect OS and storage path
    """

    # Check if running in Android or Termux
    if "termux" in sys.prefix or os.path.exists(os.path.join(home_dir, "storage")):
        download_path = os.path.join(home_dir, "storage", "shared", "Download")
    else:
        # Otherwise return Ubuntu or Windows path
        download_path = os.path.join(home_dir, "Downloads", APP_NAME)

    # Ensure the download path exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    return download_path


def clean_text(text):
    """
    Replace unwanted symbolc from a text with _ using regrex
    """
    return re.sub(r'[\\/*?:"<>|]', "_", text)


def find_url_id(url, playlist=False):
    """
    Find ID from URL using regex
    """
    if playlist:
        return re.search(r"list=([a-zA-Z0-9_-]+)", url)
    else:
        return re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    

def all_tracks(tracks):
    """
    Parse tracks from a playlist
    """
    tmp = []
    for track in tracks:
        if not track.get("videoId"):
            continue
        tmp.append({
            "title": track["title"],
            "artist":track["artists"][0]["name"] if track.get("artists") else "Unknown Artist",
            "album": track.get("album", {}).get("name", "") if track.get("album") else "",
            "video_id": track["videoId"],
            "url": f"https://music.youtube.com/watch?v={track['videoId']}"
        })
    return tmp


def download_songs(songs,target_download_folder):
    """
    Download list of songs from consumed list
    """
    for index, song in enumerate(songs, start=1):
        title = song["title"]
        artist = song["artist"]
        album = song["album"]
        video_id = song["video_id"]
        url = song["url"]

        print(f"[{index}/{len(songs)}] Processing: {artist} - {title}")

        # Fetch song release year
        year = ""
        try:
            song_details = yt.get_along(video_id)
            microformat = song_details.get("microformat", {}).get("microformatDataRenderer", {})
            publish_date = microformat.get("publishDate")
            year = publish_date.split("-")[0] if publish_date else ""
        except Exception:
            pass

        # Fetch song lyrics (synced)
        lyrics_text = fetch_lyrics(artist, title)

        # Download audio via YT-DLP
        safe_title = clean_text(title)
        safe_artist = clean_text(artist)
        
        output_filename = f"{safe_artist} - {safe_title}"
        mp3_path = os.path.join(target_download_folder, f"{output_filename}.mp3")

        opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(target_download_folder, f"{output_filename}.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Download Failed: {e}. Skipping to the next song.")
            continue

        # EasyID3 metadata tagging
        try:
            audio = EasyID3(mp3_path)
            audio["title"] = title
            audio["artist"] = artist
            if album:
                audio["album"] = album
            if year:
                audio["date"] = year
            audio.save()
        except Exception as e:
            print(f"EasyID3 Tagging Error: {e}")

        # Advanced ID3 tagging (album cover and lyrics) I USED GEMINI FOR THIS PART
        try:
            audio = ID3(mp3_path)
            try:
                results_slice = yt.search(f"{artist} {title}", filter="songs")
                if results_slice:
                    thumb = results_slice[0]["thumbnails"][-1]["url"]
                    high_res_thumb = re.sub(r'=(w\d+-h\d+|s\d+)(-\S+)?$', '=w0-h0', thumb)
                    try:
                        cover_data = requests.get(high_res_thumb, timeout=5).content
                    except Exception:
                        cover_data = requests.get(thumb, timeout=5).content
                    
                    audio.add(APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=cover_data
                    ))
            except Exception:
                pass  # Art fetching failure should not halt formatting operations

            if lyrics_text:
                audio.add(USLT(encoding=3, lang="eng", desc="Lyrics", text=lyrics_text))
                print("Saved with synced lyrics.")
            
            audio.save()
        except Exception as e:
            print(f"Advanced ID3 Tagginf Error: {e}")
    
    print(f"\nAll downloads completed successfully!")




def fetch_lyrics(artist, title):
    """
    Searches and returns synced lyrics for a given song, returns None if it fails.
    """
    for q in build_queries(artist, title):
        try:
            return syncedlyrics.search(f"{artist} - {title}", synced_only=True, providers=["musixmatch", "lrclib"])
            break
        except Exception:
            continue
    return None


def build_queries(a, t):
    """
    Builds query lyrics lookup
    """
    return [
        f"{a} - {t}",
        f"{t} - {a}",
        f"{a} - {t} lyrics",
        f"{t} - {a} lyrics",
    ]
