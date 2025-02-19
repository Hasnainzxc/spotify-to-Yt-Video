import os
import re
from functools import lru_cache

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Search

# YouTube Data API imports
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# --- Spotify Configuration ---
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
            # Build a search query using track name and artist(s)
            artists = ", ".join([artist['name'] for artist in track['artists']])
            query = f"{track['name']} {artists}"
            tracks.append(query)
    return tracks

# --- YouTube Search with Caching ---
@lru_cache(maxsize=200)
def search_youtube_video(query: str) -> str:
    """
    Searches YouTube for the given query and returns the video ID.
    Uses pytube's Search and caches results to avoid repeated network calls.
    """
    results = Search(query).results
    if results and len(results) > 1:
        # Skip the first result if necessary (e.g. if it's not ideal)
        video_id = results[1].video_id
    elif results:
        video_id = results[0].video_id
    else:
        video_id = None
    return video_id

# --- YouTube Data API Setup ---
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():
    """
    Authenticates with YouTube via OAuth2 and returns a YouTube API service instance.
    This will open a browser window for you to log in.
    """
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=8080)
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def create_youtube_playlist(youtube, title: str, description: str, privacy_status="public"):
    """
    Creates a new YouTube playlist with the specified title and description.
    Returns the playlist creation response (including the playlist ID).
    """
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": privacy_status  # Options: public, unlisted, or private
            }
        }
    )
    response = request.execute()
    return response

def add_video_to_playlist(youtube, playlist_id: str, video_id: str):
    """
    Adds a video (by video ID) to the specified YouTube playlist.
    """
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    return response

def convert_playlist(spotify_playlist_url: str):
    """
    Converts a Spotify playlist to a list of YouTube video URLs.
    This function fetches track queries from Spotify and uses the YouTube search to find matching video IDs.
    """
    print("Fetching Spotify playlist...")
    track_queries = get_spotify_tracks(spotify_playlist_url)
    youtube_links = []
    for query in track_queries:
        print(f"Searching YouTube for: {query}")
        vid_id = search_youtube_video(query)
        if vid_id:
            yt_url = f"https://www.youtube.com/watch?v={vid_id}"import os
import re
from functools import lru_cache

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Search

# YouTube Data API imports
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# --- Spotify Configuration ---
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# --- Spotify Setup using Client Credentials Flow ---
sp_auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                   client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=sp_auth)

def extract_spotify_playlist_id(playlist_url: str) -> str:
    """Extracts the playlist ID from a Spotify playlist URL."""
    match = re.search(r'open\.spotify\.com/playlist/([a-zA-Z0-9]+)', playlist_url)
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
            # Build a search query using track name and artist(s)
            artists = ", ".join([artist['name'] for artist in track['artists']])
            query = f"{track['name']} {artists}"
            tracks.append(query)
    return tracks

# --- YouTube Search with Caching ---
@lru_cache(maxsize=200)
def search_youtube_video(query: str) -> str:
    """
    Searches YouTube for the given query and returns the video ID.
    Uses pytube's Search and caches results to avoid repeated network calls.
    """
    results = Search(query).results
    if results and len(results) > 1:
        # Skip the first result if necessary (e.g. if it's not ideal)
        video_id = results[1].video_id
    elif results:
        video_id = results[0].video_id
    else:
        video_id = None
    return video_id

# --- YouTube Data API Setup ---
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():
    """
    Authenticates with YouTube via OAuth2 and returns a YouTube API service instance.
    This will open a browser window for you to log in.
    """
    # Note: The redirect URI registered in your Google Cloud Console must match
    # the URI used here. Since your Authorized Redirect URI is set to:
    # "http://localhost:8888/callback", we use port 8888.
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=8888)
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def create_youtube_playlist(youtube, title: str, description: str, privacy_status="public"):
    """
    Creates a new YouTube playlist with the specified title and description.
    Returns the playlist creation response (including the playlist ID).
    """
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": privacy_status  # Options: public, unlisted, or private
            }
        }
    )
    response = request.execute()
    return response

def add_video_to_playlist(youtube, playlist_id: str, video_id: str):
    """
    Adds a video (by video ID) to the specified YouTube playlist.
    """
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    return response

def convert_playlist(spotify_playlist_url: str):
    """
    Converts a Spotify playlist to a list of YouTube video URLs.
    This function fetches track queries from Spotify and uses the YouTube search
    to find matching video IDs.
    """
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
    # Prompt the user for the Spotify playlist URL.
    spotify_url = input("Enter Spotify playlist URL: ").strip()
    yt_links = convert_playlist(spotify_url)
    
    # Authenticate with YouTube.
    print("\nAuthenticating with YouTube...")
    youtube = get_youtube_service()
    
    # Prompt for new YouTube playlist details.
    playlist_title = input("Enter new YouTube playlist title: ").strip()
    playlist_description = input("Enter playlist description: ").strip()
    
    # Create the new YouTube playlist.
    playlist_response = create_youtube_playlist(youtube, playlist_title, playlist_description)
    playlist_id = playlist_response['id']
    print(f"\nYouTube Playlist Created! Playlist ID: {playlist_id}")
    print(f"View it here: https://www.youtube.com/playlist?list={playlist_id}")
    
    # Add each video to the YouTube playlist.
    count = 0
    for link in yt_links:
        # Extract the video ID from the URL.
        video_id = link.split("v=")[-1]
        add_video_to_playlist(youtube, playlist_id, video_id)
        count += 1
        print(f"Added video {count}/{len(yt_links)}")
    
    print(f"\nPlaylist sync complete! Total {count} videos added.")

            youtube_links.append(yt_url)
            print(f"Found: {yt_url}")
        else:
            print(f"No match found for: {query}")
    return youtube_links

if __name__ == '__main__':
    # Use descriptive prompts for user input.
    spotify_url = input("Enter Spotify playlist URL: ").strip()

    yt_links = convert_playlist(spotify_url)
    
    # Authenticate with YouTube Data API.
    print("\nAuthenticating with YouTube...")
    youtube = get_youtube_service()
    
    # Prompt user for new playlist details.
    playlist_title = input("https://www.youtube.com/watch?v=GZvk0-BnJHo&list=PLSFYbUMCjMtsUJ0MxP84hSWauxoJJyj6u&pp=gAQB").strip()
    playlist_description = input("Enter playlist description: ").strip()
    
    # Create a new YouTube playlist.
    playlist_response = create_youtube_playlist(youtube, playlist_title, playlist_description)
    playlist_id = playlist_response['id']
    print(f"\nYouTube Playlist Created! Playlist ID: {playlist_id}")
    print(f"View it here: https://www.youtube.com/playlist?list={playlist_id}")
    
    # Add each video to the newly created playlist.
    count = 0
    for link in yt_links:
        # Extract video ID from the URL.
        video_id = link.split("v=")[-1]
        add_video_to_playlist(youtube, playlist_id, video_id)
        count += 1
        print(f"Added video {count}/{len(yt_links)}")
    
    print(f"\nPlaylist sync complete! Total {count} videos added.")
