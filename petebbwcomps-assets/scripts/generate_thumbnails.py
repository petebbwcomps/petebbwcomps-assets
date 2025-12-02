import subprocess
import os
import json

# Ask user for folder at runtime
folder = input("Enter the folder containing the videos: ").strip()

# Validate input folder
if not os.path.isdir(folder):
    raise ValueError(f"Folder does not exist: {folder}")

# Output folder for thumbnails
output_folder = r"D:\0. Bruh\0. Scripts\test-site\PeteBBWComps-assets\thumbnails"
os.makedirs(output_folder, exist_ok=True)

# Allowed video extensions
video_exts = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv"}

def get_duration(video_path):
    """Uses ffprobe to get video duration in seconds."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ],
        capture_output=True,
        text=True
    )
    
    data = json.loads(result.stdout)
    if "format" in data and "duration" in data["format"]:
        return float(data["format"]["duration"])
    return 0

# Walk through all subfolders
for root, dirs, files in os.walk(folder):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in video_exts:
            full_path = os.path.join(root, file)
            base = os.path.splitext(file)[0]
            out = os.path.join(output_folder, base + ".png")
            
            # Get duration and compute halfway point
            duration = get_duration(full_path)
            timestamp = str(duration / 2 if duration > 0 else 0)
            
            # Extract frame at midpoint
            subprocess.run([
                "ffmpeg", "-y",
                "-ss", timestamp,
                "-i", full_path,
                "-vframes", "1",
                out
            ])
            
            print(f"{file}: duration={duration:.2f}s, thumbnail at t={timestamp}s")

print("Done! Thumbnails saved to:", output_folder)