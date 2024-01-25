import argparse
import json
import logging
from pathlib import Path
from collections import defaultdict

import music_tag

CSV_COLUMNS_SIZE = 4
VA_NAME = 'Various Artists'
VA_MATCH = ['various', 'va', 'v/a']

def check_va(artist: str, album_artist: str, music_file: Path) -> str:
    # main VA condition:
    # album_artist should be different from or not include artist
    if album_artist and (artist.lower() not in album_artist.lower()):
        # sanity check:
        # album_artist should already be marked as various
        va_matched = [match in album_artist.lower() for match in VA_MATCH]
        if va_matched:
            return VA_NAME
        else:
            logging.warning(f'{music_file} - artist and album_artist mismatch')
    # duet condition
    # album_artist should be different from and include artist
    elif (artist.lower() != album_artist.lower()) and (artist in album_artist):
        return album_artist
    
    return artist

def parse_folder(music_folder_path: Path) -> dict:
    # artist: {album: [song file path]}
    music_structure = defaultdict(lambda: defaultdict(lambda: list()))
    
    for music_file in music_folder_path.glob('*[!.csv]'):
        assert music_file.suffix != '.csv'

        tags = music_tag.load_file(music_file)
        song = str(music_file)
        album = tags['album'].value.strip() or 'uncategorized'
        artist = tags['artist'].value.strip() or 'uncategorized'
        album_artist = tags['albumartist'].value.strip()

        artist = check_va(artist, album_artist, music_file)

        music_structure[artist][album].append(song)

    return music_structure

def main(music_folder: str, ensure_ascii: bool) -> None:
    music_folder_path = Path(music_folder)
    music_structure = parse_folder(music_folder_path)

    output_str = json.dumps(music_structure, indent=4, ensure_ascii=ensure_ascii)
    print(output_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('music_folder')
    parser.add_argument('--ensure-ascii', action='store_true')
    
    args = parser.parse_args()
    main(args.music_folder, args.ensure_ascii)
