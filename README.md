# album-name-and-cover-fetcher
Python script to find, fetch and add album name and album cover based on Artist/Title

This Python script helps you find, fetch, and add album names and album covers to your music files based on the artist and title. It uses the Spotify API, so you will need to [create a Spotify account and obtain an API key](https://developer.spotify.com). 

Once you have your API key, point the script to the folder containing your music files. The script will then automatically update your music files with the correct album information and cover art.

How to use?
1. Download album_info_art_fetcher.py nad
2. Add your Spotify API key to the script
3. Add you music folder path to the script
4. Run it with python3 album_info_art_fetcher.py


How to find not updated tracks or tracks without Album Name?|
1. Download find_album_empty_art.sh and you are going to get the list of files without any Album Name
2. To check songs with specific album name you can modify the script by changing check_album() function
