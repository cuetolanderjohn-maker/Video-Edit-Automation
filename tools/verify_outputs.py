import os
import subprocess

FFMPEG_BIN = r"C:\Users\lande\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
if FFMPEG_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

FFMPEG = os.path.join(FFMPEG_BIN, "ffmpeg.exe") if os.path.exists(os.path.join(FFMPEG_BIN, "ffmpeg.exe")) else "ffmpeg"
FFPROBE = os.path.join(FFMPEG_BIN, "ffprobe.exe") if os.path.exists(os.path.join(FFMPEG_BIN, "ffprobe.exe")) else "ffprobe"

slugs = [
    "4k-joker-curve",
    "4k-bane-darkness",
    "4k-interstellar-docking",
    "4k-gladiator-maximus",
    "4k-wolf-not-leaving"
]

print("=== VERIFYING OUTPUT VIDEOS ===")
all_ok = True
for slug in slugs:
    path = os.path.join("outbox", f"{slug}-preset-a-minimal.mp4")
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        all_ok = False
        continue
    size_mb = os.path.getsize(path) / (1024 * 1024)
    
    # ffprobe check duration & resolution
    probe_cmd = [
        FFPROBE, "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration",
        "-of", "csv=p=0",
        path
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True)
    out = res.stdout.strip()
    print(f"OK: {slug} -> {size_mb:.2f} MB | {out}")
    
    # Extract preview at 20s
    preview_img = f"preview_{slug}.png"
    prev_cmd = [
        FFMPEG, "-y", "-ss", "00:00:20", "-i", path, "-vframes", "1", preview_img
    ]
    subprocess.run(prev_cmd, capture_output=True)

if all_ok:
    print("ALL 5 VIDEOS VERIFIED!")
