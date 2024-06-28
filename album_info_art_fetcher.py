import os
import requests
import mutagen
from mutagen.id3 import ID3, TALB, TPE1, TIT2, APIC, ID3NoHeaderError
from requests.auth import HTTPBasicAuth

# Spotify API credentials to change by user
SPOTIFY_CLIENT_ID = 'SPOTIFY_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = '<SPOTIFY_CLIENT_SECRET'

def get_spotify_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + (client_id + ":" + client_secret).encode("ascii").decode("ascii"),
    }
    data = {
        "grant_type": "client_credentials",
    }
    response = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret))
    response_data = response.json()
    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        print(f"Error obtaining access token: {response_data}")
        return None

def get_album_info_from_spotify(access_token, artist, title):
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "q": f"artist:{artist} track:{title}",
        "type": "track",
        "limit": 1,
    }
    response = requests.get(search_url, headers=headers, params=params)
    response_data = response.json()

    # Debugging: Print the response data
    print("Spotify API response:", response_data)

    if 'tracks' in response_data and response_data['tracks']['items']:
        track = response_data['tracks']['items'][0]
        album_title = track['album']['name']
        album_id = track['album']['id']
        print(f"Found album: {album_title} with ID: {album_id} for artist: {artist} and title: {title}")
        return album_title, album_id
    else:
        print(f"No suitable album found for artist: {artist} and title: {title}. Setting album to 'Single'.")
        return "Single", None

def get_cover_art_from_spotify(access_token, album_id):
    if not album_id:
        return None
    album_url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(album_url, headers=headers)
    response_data = response.json()
    if response_data.get('images'):
        cover_art_url = response_data['images'][0]['url']
        cover_art_data = requests.get(cover_art_url).content
        print(f"Found cover art for album ID: {album_id}")
        return cover_art_data
    else:
        print(f"No cover art found for album ID: {album_id}")
        return None

def update_file_metadata(file_path, access_token):
    print(f"Processing file: {file_path}")
    try:
        audio = ID3(file_path)
    except ID3NoHeaderError:
        print(f"No ID3 header found for file: {file_path}. Skipping.")
        return
    
    artist_frame = audio.get('TPE1', None)
    title_frame = audio.get('TIT2', None)
    if not artist_frame or not title_frame:
        print("Artist or title tag not found. Skipping file.")
        return
    
    artist = artist_frame.text[0] if artist_frame and isinstance(artist_frame, mutagen.id3.TextFrame) else None
    title = title_frame.text[0] if title_frame and isinstance(title_frame, mutagen.id3.TextFrame) else None
    
    if not artist or not title:
        print("Artist or title tag not correctly formatted. Skipping file.")
        return
    
    print(f"Artist: {artist}, Title: {title}")
    
    album_title, album_id = get_album_info_from_spotify(access_token, artist, title)
    
    # Update album title and cover art
    audio.delall('TALB')
    audio.add(TALB(encoding=3, text=album_title))
    
    cover_art_data = get_cover_art_from_spotify(access_token, album_id)
    if cover_art_data:
        audio.delall('APIC')
        audio.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3, desc='Cover',
            data=cover_art_data
        ))
    
    audio.save(file_path)
    print(f"Updated file: {file_path} with album: {album_title}")

def process_folder(folder_path, access_token):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.mp3', '.flac', '.ogg', '.m4a')):
                file_path = os.path.join(root, file)
                update_file_metadata(file_path, access_token)

if __name__ == "__main__":
    # Path to change by user
    folder_path = "/path/to/your/music/files"
    access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    if access_token:
        process_folder(folder_path, access_token)
    else:
        print("Failed to obtain access token. Exiting.")
