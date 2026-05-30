"""
Auralis - Command-Line Music & Playlist Downloader
CS50x Final Project - Harvard University

Author: Prince Addai Desmond | pxrr0x
Date: 30th May 2026
"""

import os
from downloaders import all_tracks, clean_text, check_system, download_songs, find_url_id
from ytmusicapi import YTMusic

try:
    # Initialize youtube music API
    yt = YTMusic()

    # Get music download folder
    download_folder = check_system()

    query = input("YT Music link / Search Query: ").strip()
    songs_to_download = []
    target_download_folder = download_folder
    # Check if the user input is a playlist
    if "list=" in query:
        print("\nParsing playlist details...")
        try:
            playlist_id = find_url_id(query, playlist=True).group(1)
            playlist_data = yt.get_playlist(playlist_id)
            tracks = playlist_data.get("tracks", [])

            # Get and clean playlist name for folder creation
            playlist_title = playlist_data.get("title", "Unknown Playlist")
            clean_playlist_title = clean_text(playlist_title)

            # Update target download folder to a sub-folder
            target_download_folder = os.path.join(download_folder, clean_playlist_title)
            if not os.path.exists(target_download_folder):
                os.makedirs(target_download_folder)
                print(f"Created playlist folder: {clean_playlist_title}")

            songs_to_download = all_tracks(tracks)
            print(f"Found {len(songs_to_download)} songs to download.\n")

            # Download songs in list
            download_songs(songs_to_download, target_download_folder)
        except Exception as e:
            print(f"Error parsing playlist: {e}")
            exit()

    # If its a single song URL or text search query
    else:
        print("\nSearching Youtube Music...")
        video_id = None

        # Check if input is a direct song video URL
        video_match = find_url_id(query)
        if video_match:
            video_id = video_match.group(1)
            try:
                song_details = yt.get_song(video_id)
                video_details = song_details.get("videoDetails", {})
                title = video_details.get("title")
                artist = video_details.get("author")
                album = ""
            except Exception as e:
                print(f"Error fetching song metadata: {e}")
                exit()
        else:
            # Standard text search
            results = yt.search(query, filter="songs")
            if not results:
                print("No songs found.")
                exit()
            song = results[0]
            title = song["title"]
            artist = song["artists"][0]["name"] if song.get("artists") else "Unknown Artist"
            album = song.get("album", {}).get("album", {}).get("name", "") if song.get("album") else ""
            video_id = song["videoId"]

        songs_to_download.append({
            "title": title,
            "artist": artist,
            "album": album,
            "video_id": video_id,
            "url": f"https://music.youtube.com/watch?v={video_id}"
        })

        # Download songs in list
        download_songs(songs_to_download, target_download_folder)
        exit()
except KeyboardInterrupt:
    print("\n")