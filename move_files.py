import shutil
import json
import argparse
import logging
from typing import List
from pathlib import Path

from get_metadata import escape

def files_to_move(output_folder_path: Path, music_structure: dict) -> List[tuple]:
    output = []
    for artist, album_dict in music_structure.items():
        for album, songs in album_dict.items():
            artist = escape(artist)
            album = escape(album)

            for song in songs:
                src = Path(song)
                dst: Path = output_folder_path / artist / album / src.name

                if dst.exists():
                    logging.warning(f'"{dst}" - path already exists, skipping...')
                else:
                    output.append((src, dst))

    return output

def move_files(src_dst: List[tuple], dry_run: bool) -> None:
    for src, dst in src_dst:
        print(f'"{src}" -> "{dst}"')

        if not dry_run:
            parent_dir = dst.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True)
                
            shutil.copy(src, dst)

def main(music_structure_file: str, output_folder: str, dry_run: bool) -> None:
    music_structure = json.loads(Path(music_structure_file).read_text())
    output_folder_path = Path(output_folder)

    src_dst = files_to_move(output_folder_path, music_structure)
    move_files(src_dst, dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('music_structure_file')
    parser.add_argument('output_folder')
    parser.add_argument('--dry-run', action='store_true')
    
    args = parser.parse_args()
    main(args.music_structure_file, args.output_folder, args.dry_run)
