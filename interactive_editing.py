import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import last_folder_helper
from batch_edit_tags import clean_title, build_new_tags

def get_current_artist(audio):
    if audio.tags is None:
        return None
    if "TPE1" in audio.tags:
        return str(audio.tags["TPE1"])
    return None

def edit_folder_tags_interactive(folder_path):
    if not os.path.isdir(folder_path):
        print("Folder not found")
        return
    mp3_files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith(".mp3"))
    if not mp3_files:
        print("No MP3 files found in folder")
        return
    changed_count = 0
    skipped_count = 0
    for filename in mp3_files:
        mp3_path = os.path.join(folder_path, filename)
        clean_name = clean_title(filename)
        print(f"\nFile:  {filename}")
        print(f"Title: {clean_name}")
        audio = MP3(mp3_path, ID3=ID3)
        current_artist = get_current_artist(audio)
        if current_artist:
            prompt = f"Artist [{current_artist}]: "
        else:
            prompt = "Artist: "
        artist_input = input(prompt).strip()
        if current_artist and not artist_input:
            artist = current_artist
        elif artist_input:
            artist = artist_input
        else:
            print("Skipped")
            skipped_count += 1
            continue
        try:
            new_tags = build_new_tags(audio.tags, clean_name, artist)
            audio.tags = new_tags
            audio.save(v2_version=3, v1=0)
            print(f"Updated: {filename} → Title: {clean_name}, Artist: {artist}")
            changed_count += 1
        except Exception as e:
            print(f"Error with file {filename}: {e}")
    print(f"\nFinished. Changed: {changed_count}, Skipped: {skipped_count}.")

if __name__ == "__main__":
    default = last_folder_helper.get_last_folder()
    folder = input(f"Folder with mp3 files ({default}): ").strip() or default
    last_folder_helper.save_last_folder(folder)
    if not folder:
        print("Folder path is required")
    else:
        edit_folder_tags_interactive(folder)

