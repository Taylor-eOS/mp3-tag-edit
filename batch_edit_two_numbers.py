import os
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TLEN, TENC, TSSE
from batch_edit_tags import build_new_tags
import last_folder_helper

def clean_title(filename):
    name = os.path.splitext(filename)[0]
    name = name.strip()
    match = re.match(r'^\d+\s*[-.\)]\s*\d+\s*[-.\)]\s*(.+)$', name)
    if match:
        return match.group(1).strip()
    return None

def edit_folder_tags(folder_path, artist_name):
    if not os.path.isdir(folder_path):
        print("Folder not found")
        return
    changed_count = 0
    skipped_count = 0
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".mp3"):
            continue
        mp3_path = os.path.join(folder_path, filename)
        clean_name = clean_title(filename)
        if clean_name is None:
            print("Skipped (wrong format):", filename)
            skipped_count += 1
            continue
        try:
            audio = MP3(mp3_path, ID3=ID3)
            new_tags = build_new_tags(audio.tags, clean_name, artist_name)
            audio.tags = new_tags
            audio.save(v2_version=3, v1=0)
            print("Updated:", filename, "→ Title:", clean_name, "Artist:", artist_name)
            changed_count += 1
        except Exception as e:
            print("Error with file", filename, ":", str(e))
    print("Finished. Changed tags on", changed_count, "files. Skipped", skipped_count, "files due to format.")

if __name__ == "__main__":
    default = last_folder_helper.get_last_folder()
    folder = input(f"Folder with mp3 files ({default}): ").strip() or default
    artist = input("Artist name for all files: ").strip() or "Michael Jackson"
    last_folder_helper.save_last_folder(folder)
    if not folder or not artist:
        print("Folder path and artist name are required")
    else:
        edit_folder_tags(folder, artist)

