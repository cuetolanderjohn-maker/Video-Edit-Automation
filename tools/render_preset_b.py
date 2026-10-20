import os
import sys
import json
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont

FFMPEG_BIN = r"C:\Users\lande\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
if FFMPEG_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

FFMPEG = os.path.join(FFMPEG_BIN, "ffmpeg.exe") if os.path.exists(os.path.join(FFMPEG_BIN, "ffmpeg.exe")) else "ffmpeg"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_SEMI = r"C:\Windows\Fonts\segoeui.ttf"

def chunk_words(words_list, max_words=3, max_gap=0.3):
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
            chunks.append({
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["end"],
                "text": " ".join(item["text"] for item in current_chunk).strip().upper()
            })
            current_chunk = [w]
        else:
            current_chunk.append(w)
            
    if current_chunk:
        chunks.append({
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["end"],
            "text": " ".join(item["text"] for item in current_chunk).strip().upper()
        })
    return chunks

def hex_to_ass_color(hex_color, alpha="00"):
    hex_color = hex_color.lstrip("#")
    r = hex_color[0:2]
    g = hex_color[2:4]
    b = hex_color[4:6]
    return f"&H{alpha}{b}{g}{r}"

def format_ass_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs == 100:
        cs = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"

def generate_ass_subtitles(chunks, ass_path, glow_color_hex="#F59E0B"):
    ass_glow = hex_to_ass_color(glow_color_hex)
    
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,54,&H00FFFFFF,&H00FFFFFF,{ass_glow},&HA0000000,1,0,0,0,100,100,1.2,0,1,4.5,2.5,2,40,40,470,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for c in chunks:
        start_t = max(0.0, c["start"] - 0.04)
        end_t = max(start_t + 0.25, c["end"])
        t1 = format_ass_time(start_t)
        t2 = format_ass_time(end_t)
        clean_text = c["text"].replace("{", "").replace("}", "")
        events.append(f"Dialogue: 0,{t1},{t2},Default,,0,0,0,,{clean_text}")
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

def create_overlay(overlay_path, bottom_attribution="", show_banner=False, pre_text="", accent_text="", post_text="", accent_color=(217, 119, 6), sub_title=""):
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_h1 = ImageFont.truetype(FONT_BOLD, 40)
    font_sub = ImageFont.truetype(FONT_BOLD, 22)
    font_attr = ImageFont.truetype(FONT_BOLD, 20)
    
    # If banner is explicitly enabled in future
    if show_banner:
        card_w = 980
        card_h = 164
        card_x0 = (1080 - card_w) // 2
        card_y0 = 135
        card_x1 = card_x0 + card_w
        card_y1 = card_y0 + card_h
        
        for offset in range(5, 0, -1):
            draw.rounded_rectangle(
                [card_x0 - offset, card_y0 - offset + 4, card_x1 + offset, card_y1 + offset + 4],
                radius=18,
                fill=(0, 0, 0, 18)
            )
        draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=18, fill=(255, 255, 255, 255))
        
        full_line1 = []
        if pre_text: full_line1.append((pre_text, (17, 24, 39, 255)))
        if accent_text: full_line1.append((accent_text, (*accent_color, 255)))
        if post_text: full_line1.append((post_text, (17, 24, 39, 255)))
        
        total_w1 = 0
        segment_widths = []
        for txt, col in full_line1:
            bbox = draw.textbbox((0, 0), txt, font=font_h1)
            w = bbox[2] - bbox[0]
            segment_widths.append(w)
            total_w1 += w
            
        cur_x = (1080 - total_w1) // 2
        text_y1 = card_y0 + 34
        for i, (txt, col) in enumerate(full_line1):
            draw.text((cur_x, text_y1), txt, font=font_h1, fill=col)
            cur_x += segment_widths[i]
            
        if sub_title:
            bbox_sub = draw.textbbox((0, 0), sub_title, font=font_sub)
            w_sub = bbox_sub[2] - bbox_sub[0]
            x_sub = (1080 - w_sub) // 2
            draw.text((x_sub, card_y0 + 102), sub_title, font=font_sub, fill=(75, 85, 99, 255))
            
    # Bottom attribution tag
    if bottom_attribution:
        bbox_attr = draw.textbbox((0, 0), bottom_attribution, font=font_attr)
        w_attr = bbox_attr[2] - bbox_attr[0]
        pill_w = w_attr + 48
        pill_h = 44
        px0 = (1080 - pill_w) // 2
        py0 = 1650
        draw.rounded_rectangle([px0, py0, px0 + pill_w, py0 + pill_h], radius=22, fill=(15, 23, 42, 220), outline=(255, 255, 255, 45), width=1)
        draw.text((px0 + 24, py0 + 10), bottom_attribution, font=font_attr, fill=(241, 245, 249, 240))
        
    img.save(overlay_path, "PNG")

def render_clip(slug, header_config, show_banner=False):
    video_in = os.path.join("inbox", f"{slug}.mp4")
    json_in = os.path.join("inbox", f"{slug}.json")
    video_out_v2 = os.path.join("outbox", f"{slug}-v2.mp4")
    video_out_preset_b = os.path.join("outbox", f"{slug}-preset-b.mp4")
    
    if not os.path.exists(video_in) or not os.path.exists(json_in):
        print(f"Skipping {slug}: missing video or json")
        return
        
    print(f"\n==========================================")
    print(f"Rendering {slug} without banner (v2)...")
    print(f"==========================================")
    
    with open(json_in, "r", encoding="utf-8") as f:
        data = json.load(f)
    words = data.get("words", [])
    chunks = chunk_words(words)
    print(f"Loaded {len(words)} words -> {len(chunks)} subtitle chunks")
    
    ass_path = os.path.abspath(f"scratch_{slug}.ass")
    overlay_path = os.path.abspath(f"scratch_{slug}_overlay.png")
    
    generate_ass_subtitles(chunks, ass_path, glow_color_hex=header_config.get("glow_hex", "#F59E0B"))
    create_overlay(
        overlay_path,
        bottom_attribution=header_config.get("attribution", ""),
        show_banner=show_banner
    )
    
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    overlay_escaped = overlay_path.replace("\\", "/").replace(":", "\\:")
    
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:4,eq=brightness=-0.38[bg]; "
        "[0:v]crop=in_h:in_h:(in_w-in_h)/2:0,scale=1080:1080[fg]; "
        "[bg][fg]overlay=0:420[comp]; "
        f"[comp][1:v]overlay=0:0[with_hdr]; "
        f"[with_hdr]subtitles='{ass_escaped}'[outv]; "
        "[0:a]loudnorm=I=-14:LRA=7:tp=-1.5[outa]"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-i", video_in,
        "-i", overlay_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        video_out_v2
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(ass_path): os.remove(ass_path)
    if os.path.exists(overlay_path): os.remove(overlay_path)
    
    if res.returncode != 0:
        print(f"Error rendering {slug}:\n{res.stderr[-1000:]}")
    else:
        # Also copy to preset-b name so both are up to date
        shutil.copyfile(video_out_v2, video_out_preset_b)
        size_mb = os.path.getsize(video_out_v2) / (1024 * 1024)
        print(f"SUCCESS: Rendered {video_out_v2} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    configs = {
        "fight-club-tyler-durden": {
            "glow_hex": "#FACC15", # Neon Toxic Yellow
            "attribution": "FIGHT CLUB (1999) • TYLER DURDEN"
        },
        "dark-knight-the-joker": {
            "glow_hex": "#C084FC", # Joker Violet
            "attribution": "THE DARK KNIGHT (2008) • THE JOKER"
        },
        "whiplash-fletcher": {
            "glow_hex": "#F59E0B", # Intense Jazz Brass Gold
            "attribution": "WHIPLASH (2014) • J.K. SIMMONS & MILES TELLER"
        },
        "interstellar-farmer": {
            "glow_hex": "#38BDF8", # Cosmic Sky Blue
            "attribution": "INTERSTELLAR (2014) • CHRISTOPHER NOLAN"
        },
        "fight-club-theater-destruction": {
            "glow_hex": "#EF4444", # Project Mayhem Crimson
            "attribution": "FIGHT CLUB (1999) • PROJECT MAYHEM"
        }
    }
    
    for slug, cfg in configs.items():
        render_clip(slug, cfg, show_banner=False)
