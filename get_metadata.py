import argparse
import json
import logging
from typing import List
from pathlib import Path
from collections import defaultdict

from parsing.parse_csv import parse_csv_simple
from parsing.parse_folder import parse_folder


def escape(song_name: str) -> str:
    # approximate list of characters YouTube music
    # doesn't like in track names
    to_escape = "\"'&?/:>"
    escaped_with = "_" * len(to_escape)
    table = str.maketrans(to_escape, escaped_with)
    escaped_song_name = song_name.translate(table)

    return escaped_song_name

def match_file_name(song_name: str, duplicate_songs: dict, songs_set: set) -> str:
    # file names will not have certain characters
    file_name = f'{escape(song_name)}'

    # if file names repeat, they will have a suffix:
    # Song Name.mp3, Song Name(1).mp3, ...
    # the number in this suffix matches track order in csv.
    # checking for duplication level
    if song_name in songs_set:
        duplicate_songs[song_name] += 1
    else:
        songs_set.add(song_name)
    duplication_level = duplicate_songs[song_name]

    # trying to match the method that YouTube is using
    file_name = f'{escape(song_name)}'.lower().strip()
    if duplication_level:
        file_name += f'({duplication_level})'
    
    return file_name

def find_song_metadata(
        csv_music_list: List[dict],
        unknown_song_path: Path
    ) -> tuple:
    duplicate_songs = defaultdict(lambda: 0)
    songs_set = set()

    file_name = unknown_song_path.stem.lower().strip()
    artist = None
    album = None

    for row in csv_music_list:
        c_artist = row['artist']
        c_album = row['album']
        c_song = row['song']

        # trying to match how file names look on disk and in csv
        expected_file_name = match_file_name(c_song, duplicate_songs, songs_set)

        if file_name == expected_file_name:
            artist = c_artist
            album = c_album

            # # sanity check that the song was indeed uncategorized
            # assert str(unknown_song_path) not in folder_music_structure[c_artist][c_album]

            assert all([artist, album])
            break

    if not all([artist, album]):
        logging.warning(f'"{unknown_song_path}" - song metadata not found')

    return artist, album

def fix_uncategorized(uncategorized: List[str], csv_music_list: List[dict]) -> dict:
    fixed_uncategorized = defaultdict(lambda: defaultdict(lambda: list()))

    for unknown_song_file in uncategorized:
        unknown_song_file_path = Path(unknown_song_file)

        artist, album = find_song_metadata(csv_music_list, unknown_song_file_path)
        if all([artist, album]):
            fixed_uncategorized[artist][album].append(unknown_song_file)
            
    return fixed_uncategorized

def merge_fixed(folder_data: dict, csv_data: List[dict]) -> None:
    uncategorized = folder_data.pop('uncategorized')['uncategorized']
    fixed_uncategorized = fix_uncategorized(uncategorized, csv_data)

    for artist, album_dict in fixed_uncategorized.items():
        for album, songs in album_dict.items():
            present_album = folder_data.get(artist, {}).get(album)
            if present_album:
                folder_data[artist][album].extend(songs)
            else:
                folder_data[artist][album] = songs

def get_metadata(csv_file_path: Path, music_folder_path: Path):
    # music files tags are considered primary source of truth
    # since csv song names and file names do not correspond 1:1.
    folder_data = parse_folder(music_folder_path)
    # but some files might be missing tags alltoghether
    # therefore let's take missing information from csv
    csv_data = parse_csv_simple(csv_file_path)

    merge_fixed(folder_data, csv_data)

    return folder_data    

def main(music_folder: str, ensure_ascii: bool) -> None:
    music_folder_path = Path(music_folder)
    csv_file_path = next(music_folder_path.glob('*.csv'))
    music_structure = get_metadata(csv_file_path, music_folder_path)

    output_str = json.dumps(music_structure, indent=4, ensure_ascii=ensure_ascii)
    print(output_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('music_folder')
    parser.add_argument('--ensure-ascii', action='store_true')
    
    args = parser.parse_args()
    main(args.music_folder, args.ensure_ascii)
