 #!/bin/bash

# Path to your music folder
MUSIC_FOLDER="/path/to/your/folder/with/music"

check_album() {
    file="$1"
    album=$(ffmpeg -i "$file" 2>&1 | grep -oP 'album\s*:\s*\K.*' | head -1)
    if [ -z "$album" ]; then
        echo "$file"
    fi
}

export -f check_album
find "$MUSIC_FOLDER" -type f \( -iname "*.mp3" -o -iname "*.flac" -o -iname "*.m4a" \) -exec bash -c 'check_album "$0"' {} \;
