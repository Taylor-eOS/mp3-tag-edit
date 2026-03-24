import os
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TLEN, TENC, TSSE, TALB
import last_folder_helper

def clean_title(filename):
    name = os.path.splitext(filename)[0]
    name = name.strip()
    name = re.sub(r'^\d+\s*[-.\)]\s*', '', name)
    name = re.sub(r'^\d+\.\s*', '', name)
    name = name.strip()
    return name

def build_new_tags(old_tags, clean_name, artist_name, update_artist):
    new_tags = ID3()
    new_tags.add(TIT2(encoding=3, text=clean_name))
    if update_artist and artist_name:
        new_tags.add(TPE1(encoding=3, text=artist_name))
    if old_tags is not None:
        if "TALB" in old_tags:
            new_tags.add(TALB(encoding=3, text=old_tags["TALB"].text[0]))
        if "TRCK" in old_tags:
            new_tags.add(TRCK(encoding=3, text=old_tags["TRCK"].text[0]))
        if "TLEN" in old_tags:
            new_tags.add(TLEN(encoding=3, text=old_tags["TLEN"].text[0]))
        if "TENC" in old_tags:
            new_tags.add(TENC(encoding=3, text=old_tags["TENC"].text[0]))
        if "TSSE" in old_tags:
            new_tags.add(TSSE(encoding=3, text=old_tags["TSSE"].text[0]))
    return new_tags

def edit_folder_tags(folder_path, artist_name, update_artist):
    if not os.path.isdir(folder_path):
        print("Folder not found")
        return
    changed_count = 0
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".mp3"):
            continue
        mp3_path = os.path.join(folder_path, filename)
        try:
            audio = MP3(mp3_path, ID3=ID3)
            clean_name = clean_title(filename)
            new_tags = build_new_tags(audio.tags, clean_name, artist_name, update_artist)
            audio.tags = new_tags
            audio.save(v2_version=3, v1=0)
            if update_artist:
                print("Updated:", filename, "→ Title:", clean_name, "Artist:", artist_name)
            else:
                print("Updated:", filename, "→ Title:", clean_name)
            changed_count += 1
        except Exception as e:
            print("Error with file", filename, ":", str(e))
    print("Finished. Changed tags on", changed_count, "files.")

if __name__ == "__main__":
    default = last_folder_helper.get_last_folder()
    folder = input(f"Folder with mp3 files ({default}): ").strip() or default
    artist = input("Artist name for all files (empty for none): ").strip()
    update_artist = bool(artist)
    if not artist:
        artist = "Michael Jackson"  #fallback, but will not be used
    last_folder_helper.save_last_folder(folder)
    if not folder:
        print("Folder path is required")
    else:
        edit_folder_tags(folder, artist, update_artist)

