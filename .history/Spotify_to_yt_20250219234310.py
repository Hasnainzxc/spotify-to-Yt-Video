import os
import re
from functools import lru_cache

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Search  # pytube's Search scrapes YouTube results
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Your Spotify credentials are set in your .env file
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# --- Spotify Setup using Client Credentials Flow ---
sp_auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                   client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=sp_auth)

def extract_spotify_playlist_id(playlist_url: str) -> str:
    """Extracts the playlist ID from a Spotify playlist URL."""
    match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Spotify playlist URL")

def get_spotify_tracks(playlist_url: str):
    """Fetches track names and artist(s) from a Spotify playlist."""
    playlist_id = extract_spotify_playlist_id(playlist_url)
    results = sp.playlist(playlist_id)
    tracks = []
    for item in results['tracks']['items']:
        track = item['track']
        if track:
            # Concatenate track name and artists for a better search query.
            artists = ", ".join([artist['name'] for artist in track['artists']])
            query = f"{track['name']} {artists}"
            tracks.append(query)
    return tracks

# --- YouTube Search with Caching ---
@lru_cache(maxsize=200)
def search_youtube_video(query: str) -> str:
    """
    Searches YouTube for the given query and returns the video ID.
    The lru_cache decorator caches results to avoid repeated searches.
    """
    results = Search(query).results
    if results and len(results) > 1:
        # Skip the very first result if needed (if it isn't a proper video)
        video_id = results[1].video_id
    elif results:
        video_id = results[0].video_id
    else:
        video_id = None
    return video_id

def convert_playlist(spotify_playlist_url: str):
    """Converts a Spotify playlist to a list of YouTube video URLs."""
    print("Fetching Spotify playlist...")
    track_queries = get_spotify_tracks(spotify_playlist_url)
    youtube_links = []
    for query in track_queries:
        print(f"Searching YouTube for: {query}")
        vid_id = search_youtube_video(query)
        if vid_id:
            yt_url = f"https://www.youtube.com/watch?v={vid_id}"
            youtube_links.append(yt_url)
            print(f"Found: {yt_url}")
        else:
            print(f"No match found for: {query}")
    return youtube_links

if __name__ == '__main__':
    # Example usage – replace with your Spotify playlist URL
    spotify_url = input("https://open.spotify.com/playlist/5eXhQquA0TdhcJtfNHhDZF?si=5c1c07f827e9403a").strip()
    yt_links = convert_playlist(spotify_url)
    print("\nYouTube video links:")
    for link in yt_links:
        print(link)
