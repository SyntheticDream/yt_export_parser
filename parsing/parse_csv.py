import argparse
import csv
import json
from typing import List
from pathlib import Path
from collections import defaultdict

CSV_COLUMNS_SIZE = 4

def parse_csv_simple(csv_file_path: Path) -> List[dict]:
    # [{song, album, artist, length}]

    reader = csv.DictReader(csv_file_path.open(encoding='utf-8'))
    reader.fieldnames = ['song', 'album', 'artist', 'length']
    output = [{k: v.strip() for k, v in r.items()} for r in reader]

    return output

def parse_csv(csv_file_path: Path) -> dict:
    # artist: {album: [song name]}
    music_structure = defaultdict(lambda: defaultdict(lambda: list()))

    reader = csv.reader(csv_file_path.open(encoding='utf-8'))
    next(reader) # skip header
    for row in reader:
        assert CSV_COLUMNS_SIZE == len(row)

        parsed = list(map(lambda x: x.strip().title(), row))
        song, album, artist, _ = parsed

        music_structure[artist][album].append(song)

    return music_structure

def main(music_folder: str, ensure_ascii: bool) -> None:
    csv_file_path = next(Path(music_folder).glob('*.csv'))
    music_structure = parse_csv(csv_file_path)

    output_str = json.dumps(music_structure, indent=4, ensure_ascii=ensure_ascii)
    print(output_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('music_folder')
    parser.add_argument('--ensure-ascii', action='store_true')
    
    args = parser.parse_args()
    main(args.music_folder, args.ensure_ascii)
