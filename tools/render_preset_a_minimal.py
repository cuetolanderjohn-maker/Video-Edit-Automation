import os
import sys
import json
import subprocess

FFMPEG_BIN = r"C:\Users\lande\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
if FFMPEG_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

FFMPEG = os.path.join(FFMPEG_BIN, "ffmpeg.exe") if os.path.exists(os.path.join(FFMPEG_BIN, "ffmpeg.exe")) else "ffmpeg"

HELPERS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "but", "or",
    "nor", "so", "yet", "is", "are", "was", "were", "be", "been", "being",
    "it", "its", "it's", "this", "that", "these", "those", "my", "your", "his",
    "her", "our", "their", "we", "you", "they", "he", "she", "me", "him", "us",
    "them", "with", "from", "by", "as", "if", "not", "no"
}

def style_preset_a_text(text):
    """Preset A hierarchy: UPPERCASE BOLD for keywords, smaller lowercase for helper words."""
    words = text.strip().split()
    styled_tokens = []
    for w in words:
        clean = w.strip(".,!?:;\"'()[]{}").lower()
        if clean in HELPERS and len(clean) <= 4:
            # Helper word: smaller lowercase, soft muted gray
            styled_tokens.append(f"{{\\b0\\fs44\\c&H00D1D5DB&}}{w.lower()}{{\\r}}")
        else:
            # Emphasized keyword: large uppercase bold, pure white
            styled_tokens.append(f"{{\\b1\\fs56\\c&H00FFFFFF&}}{w.upper()}{{\\r}}")
    return " ".join(styled_tokens)

def chunk_words(words_list, max_words=3, max_gap=0.35):
    chunks = []
    current_chunk = []
    
    for i, w in enumerate(words_list):
        if not current_chunk:
            current_chunk.append(w)
            continue
            
        gap = w["start"] - current_chunk[-1]["end"]
        last_text = current_chunk[-1]["text"]
        has_punctuation = any(last_text.endswith(p) for p in [".", "?", "!", ",", ";"])
        
        if len(current_chunk) >= max_words or gap > max_gap or has_punctuation:
            raw_text = " ".join(item["text"] for item in current_chunk).strip()
            chunks.append({
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["end"],
                "text": style_preset_a_text(raw_text)
            })
            current_chunk = [w]
        else:
            current_chunk.append(w)
            
    if current_chunk:
        raw_text = " ".join(item["text"] for item in current_chunk).strip()
        chunks.append({
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["end"],
            "text": style_preset_a_text(raw_text)
        })
    return chunks

def format_ass_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs == 100: cs = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"

def generate_preset_a_ass(chunks, ass_path):
    """Generate Preset A subtitles: pure white with dark drop shadow and typographic hierarchy."""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,1,0,0,0,100,100,1.2,0,1,3.8,2.8,2,40,40,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for c in chunks:
        start_t = max(0.0, c["start"] - 0.04)
        end_t = max(start_t + 0.25, c["end"])
        t1 = format_ass_time(start_t)
        t2 = format_ass_time(end_t)
        events.append(f"Dialogue: 0,{t1},{t2},Default,,0,0,0,,{c['text']}")
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

def render_preset_a_minimal(slug):
    """Render Preset A with strict minimalist layout: NO titles/banners whatsoever."""
    video_in = os.path.join("inbox", f"{slug}.mp4")
    json_in = os.path.join("inbox", f"{slug}.json")
    video_out = os.path.join("outbox", f"{slug}-preset-a-minimal.mp4")
    
    if not os.path.exists(video_in) or not os.path.exists(json_in):
        print(f"Skipping {slug}: missing video or json")
        return
        
    print(f"\n==========================================")
    print(f"Rendering {slug} (Preset A Minimalist - NO TITLES)...")
    print(f"==========================================")
    
    with open(json_in, "r", encoding="utf-8") as f:
        data = json.load(f)
    words = data.get("words", [])
    chunks = chunk_words(words)
    print(f"Loaded {len(words)} words -> {len(chunks)} subtitle chunks")
    
    ass_path = os.path.abspath(f"scratch_{slug}_a.ass")
    generate_preset_a_ass(chunks, ass_path)
    
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    
    # Filtergraph:
    # 1. Background: scale to 1080x1920, heavy boxblur, dimmed (-0.38 brightness)
    # 2. Foreground: centered 1080x1080 crop, centered vertically at y=420
    # 3. Subtitles: Preset A Ass subtitles burned directly
    # 4. Audio: loudnorm (-14 LUFS)
    # NOTE: ZERO title cards, ZERO overlays, ZERO banners.
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:4,eq=brightness=-0.38[bg]; "
        "[0:v]crop=in_h:in_h:(in_w-in_h)/2:0,scale=1080:1080[fg]; "
        "[bg][fg]overlay=0:420[comp]; "
        f"[comp]subtitles='{ass_escaped}'[outv]; "
        "[0:a]loudnorm=I=-14:LRA=7:tp=-1.5[outa]"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-i", video_in,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        video_out
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(ass_path): os.remove(ass_path)
    
    if res.returncode != 0:
        print(f"Error rendering {slug}:\n{res.stderr[-1000:]}")
    else:
        size_mb = os.path.getsize(video_out) / (1024 * 1024)
        print(f"SUCCESS: Rendered {video_out} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    slugs = [
        "4k-joker-curve",
        "4k-bane-darkness",
        "4k-interstellar-docking",
        "4k-gladiator-maximus",
        "4k-wolf-not-leaving"
    ]
    for s in slugs:
        render_preset_a_minimal(s)
