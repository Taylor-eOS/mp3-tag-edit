import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import last_folder_helper

def remove_images_from_folder(folder_path):
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
            if audio.tags is None:
                audio.add_tags()
            if "APIC:" in audio.tags:
                del audio.tags["APIC:"]
            keys_to_remove = [key for key in audio.tags.keys() if key.startswith("APIC")]
            for key in keys_to_remove:
                del audio.tags[key]
            audio.save(v2_version=3, v1=2)
            print("Removed image from:", filename)
            changed_count += 1
        except Exception as e:
            print("Error with file", filename, ":", str(e))
    print("Finished. Removed images from", changed_count, "files.")

if __name__ == "__main__":
    default = last_folder_helper.get_last_folder()
    folder = input(f"Folder with mp3 files ({default}): ").strip() or default
    last_folder_helper.save_last_folder(folder)
    if not folder:
        print("Folder path is required")
    else:
        remove_images_from_folder(folder)

