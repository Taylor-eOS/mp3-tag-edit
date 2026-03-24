import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TLEN, TENC, TSSE
from mutagen.mp4 import MP4, MP4Cover
import last_folder_helper
import re

def clean_title(filename):
    name = os.path.splitext(filename)[0]
    name = name.strip()
    name = re.sub(r'^\d+\s*[-.\)]\s*', '', name)
    name = re.sub(r'^\d+\.\s*', '', name)
    name = name.strip()
    return name

def build_new_id3_tags(old_tags, clean_name, artist_name):
    new_tags = ID3()
    new_tags.add(TIT2(encoding=3, text=clean_name))
    new_tags.add(TPE1(encoding=3, text=artist_name))
    if old_tags is not None:
        for tag in ["TRCK", "TLEN", "TENC", "TSSE"]:
            if tag in old_tags:
                new_tags.add(old_tags[tag])
    return new_tags

def build_new_mp4_tags(old_tags, clean_name, artist_name):
    new_tags = {}
    new_tags["\xa9nam"] = clean_name
    new_tags["\xa9ART"] = artist_name
    if old_tags is not None:
        for key in ["\xa9alb", "trkn", "disk", "\xa9day", "\xa9gen", "\xa9wrt", "covr"]:
            if key in old_tags:
                new_tags[key] = old_tags[key]
    return new_tags

def edit_folder_tags(folder_path, artist_name):
    if not os.path.isdir(folder_path):
        print("Folder not found")
        return
    changed_count = 0
    for filename in os.listdir(folder_path):
        if not (filename.lower().endswith(".mp3") or filename.lower().endswith(".m4a")):
            continue
        mp3_path = os.path.join(folder_path, filename)
        try:
            clean_name = clean_title(filename)
            if filename.lower().endswith(".mp3"):
                audio = MP3(mp3_path, ID3=ID3)
                new_tags = build_new_id3_tags(audio.tags, clean_name, artist_name)
                audio.tags = new_tags
                audio.save(v2_version=3, v1=0)
            else:
                audio = MP4(mp3_path)
                new_tags = build_new_mp4_tags(audio.tags, clean_name, artist_name)
                audio.tags = new_tags
                audio.save()
            print("Updated:", filename, "→ Title:", clean_name, "Artist:", artist_name)
            changed_count += 1
        except Exception as e:
            print("Error with file", filename, ":", str(e))
    print("Finished. Changed tags on", changed_count, "files.")

if __name__ == "__main__":
    default = last_folder_helper.get_last_folder()
    folder = input(f"Folder with mp3 files ({default}): ").strip() or default
    artist = input("Artist name for all files: ").strip() or "Michael Jackson"
    last_folder_helper.save_last_folder(folder)
    if not folder or not artist:
        print("Folder path and artist name are required")
    else:
        edit_folder_tags(folder, artist)

