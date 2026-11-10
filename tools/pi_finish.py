"""Prophetic Implication finished film in the new style (10 Nov 2026): intro section + clean film with
pi_captions.py captions (flame subtitles <=5 words, point cards, current-point label) + channel logo, no lower-third bar.

Run from the book's plans folder:
  python3 pi_finish.py <storyboard.json> <intro_section.mp4> <clean.mp4> <logo.png> <out.mp4> [fontsdir]
On Windows run through win\\winrun.py (CapCut ffmpeg, NVENC). The captions are drawn with ffmpeg's ass filter (libass).
"""
import os, subprocess, sys

def main(a):
    sb, intro, clean, logo, out = a[:5]
    fonts = a[5] if len(a) > 5 else '../../../_tools/fonts'
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, 'pi_captions.py'), sb, 'windows.json', 'words.json', 'pi_clean.ass'], check=True)
    fonts = fonts.replace('\\', '/')
    g = (f"[0:v]fps=24,scale=1920:1080,setsar=1,format=yuv420p[iv];[0:a]aresample=48000,aformat=channel_layouts=stereo[ia];"
         f"[1:v]fps=24,ass=filename=pi_clean.ass:fontsdir={fonts}[cv];[cv][2:v]overlay=0:0:shortest=1,format=yuv420p[fv];"
         f"[1:a]aresample=48000,aformat=channel_layouts=stereo[fa];[iv][ia][fv][fa]concat=n=2:v=1:a=1[v][a]")
    tmp = out + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', intro, '-i', clean, '-loop', '1', '-i', logo,
                    '-filter_complex', g, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, out)
    print('wrote', out)

if __name__ == '__main__':
    main(sys.argv[1:])
