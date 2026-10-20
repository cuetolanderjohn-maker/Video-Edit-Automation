import os
import subprocess

FFMPEG_BIN = r"C:\Users\lande\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
if FFMPEG_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

clips = [
    ("4k-bane-darkness", "https://www.youtube.com/watch?v=QuWsOHIlbfE", "*02:49-03:34"),
    ("4k-interstellar-docking", "https://www.youtube.com/watch?v=onVhbeY7nLM", "*00:42-01:27"),
    ("4k-gladiator-maximus", "https://www.youtube.com/watch?v=E8e1frSahkc", "*02:30-03:15"),
    ("4k-wolf-not-leaving", "https://www.youtube.com/watch?v=lzAwDUoZwfo", "*04:55-05:40"),
]

for slug, url, section in clips:
    out_file = os.path.join("inbox", f"{slug}.mp4")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 10 * 1024 * 1024:
        print(f"Already exists: {out_file}")
        continue
    print(f"\n==========================================")
    print(f"Downloading 4K section for {slug} ({section})...")
    print(f"==========================================")
    cmd = [
        "python", "-m", "yt_dlp",
        "--download-sections", section,
        "-f", "313+140/bestvideo[height>=1440]+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", out_file,
        url
    ]
    subprocess.run(cmd, check=True)
    print(f"Finished {slug} -> {out_file}")
