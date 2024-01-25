# YouTube Music - export parser script

If you tried to export your tracks from YouTube Music (for example,
albums you purchased in Google Play, or albums you uploaded yourself),
you might have noticed that exported tracks are all stuffed together into single archive file, sometimes with metadata (tags for album artist,
song name, etc) missing completely for certain tracks.

This script attemts to move tracks into a newly created folder hierchy
categorized by artist and album, where you can manage them more easily.

## Script logic

* Collect metadata about tracks
  * From CSV (which is often unreliable)
  * From files themselves
* Detect compilation albums (various artists)
* Build music files structure in JSON format
* Move tracks to separate folders by artist and album

### Problem with Google's CSV file

The CSV file seems to only contain information about: `song name`, `album`,
`artist` and `track length`. And in case of special characters present in track
name or in case of duplicate tracks names, CSV file entries for `song` do not
match the file names. Also, `artist` here refers to track artist, not album
artist, which in case of compilation albums does not give much information.

So it might have been a good idea to ditch this file and use metadata embedded
in tracks themselves in form of various tags, but some tracks (mostly purchased
in my experience) do not feature any tags at all. So I've decided to use tags
as a source of truth with CSV as a backup to try to re-collect the data.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python get_metadata.py exported_folder > metadata.json
# use --ensure-ascii parameter when in windows terminal

python move_files.py metadata.json output_folder
# use --dry-run parameter to preview action
```
