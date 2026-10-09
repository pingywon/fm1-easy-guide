#!/usr/bin/env python3
"""Builds docs/ (the GitHub Pages one-pager) and copies the PDF + thumbnails."""
import os, shutil, subprocess

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = open(os.path.join(HERE, "VERSION")).read().strip()
DOCS = os.path.join(HERE, "docs")
DEMO = "https://fm1-demo.pingywon.workers.dev"
THUMBS = (1, 12, 21)  # cover · an ENV lesson · how a beat works

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>FM-1 Easy Guide</title>
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%%3E%%3Crect width='32' height='32' rx='7' fill='%%23111'/%%3E%%3Ccircle cx='12' cy='22' r='5' fill='%%23fff'/%%3E%%3Crect x='15' y='6' width='3' height='16' fill='%%23fff'/%%3E%%3C/svg%%3E">
<style>
* { box-sizing: border-box; }
body { margin: 0; background: #fff; color: #111; font-family: system-ui, sans-serif; font-size: 18px; line-height: 1.5; }
.wrap { max-width: 780px; margin: 0 auto; padding: 44px 18px 48px; }
h1 { font-size: 40px; line-height: 1.05; margin: 0 0 10px; }
p { margin: 0 0 14px; color: #333; }
b { color: #111; }
.btns { display: flex; gap: 10px; flex-wrap: wrap; margin: 22px 0 8px; }
.btn { font-weight: 700; font-size: 17px; padding: 12px 18px; border: 2.5px solid #111; border-radius: 10px;
       text-decoration: none; color: #111; box-shadow: 0 3px 0 #111; background: #fff; }
.btn.dark { background: #111; color: #fff; }
.thumbs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 26px 0 6px; }
.thumbs img { width: 100%%; border: 2px solid #111; border-radius: 8px; }
.small { font-size: 14px; color: #666; }
footer { margin-top: 34px; padding-top: 14px; border-top: 2px solid #111; font-size: 14px; color: #555; }
@media (max-width: 520px) { h1 { font-size: 30px; } .thumbs { gap: 8px; } }
</style></head><body><div class="wrap">
<h1>FM-1 Easy Guide</h1>
<p><b>The official manual for the M-VAVE FM-1 pocket synthesizer is genuinely hard to read</b> — dense tables,
translated phrasing, and it predates the firmware that changed how the sequencer works.</p>
<p>This project breaks the whole machine down into <b>plain-words, interactive lessons you can follow along with</b>:
a free 31-page guide where every page is one idea with tick-box steps, and a clickable on-screen FM-1 that makes
real sound while it walks you through the buttons, your first sounds and your first beat. No music knowledge needed.</p>
<div class="btns">
  <a class="btn dark" href="%(demo)s">Try the follow-along demo</a>
  <a class="btn" href="FM-1-Easy-Guide.pdf">Read the guide (PDF)</a>
  <a class="btn" href="https://github.com/pingywon/fm1-easy-guide">GitHub</a>
</div>
<p class="small">The PDF prints fine in black &amp; white. The demo runs in any modern browser, sound and all.</p>
<div class="thumbs">%(thumbs)s</div>
<p class="small">Three of the 31 pages: the cover, a lesson, and how a beat works.</p>
<footer>FM-1 Easy Guide · v%(v)s · unofficial — not made by or affiliated with M-VAVE · MIT licensed</footer>
</div></body></html>
"""


def main():
    shutil.rmtree(DOCS, ignore_errors=True)
    os.makedirs(DOCS)
    pdf = os.path.join(HERE, "FM-1-Easy-Guide.pdf")
    shutil.copy(pdf, DOCS)
    tags = []
    for p in THUMBS:
        subprocess.run(["pdftoppm", "-r", "64", "-png", "-f", str(p), "-l", str(p),
                        pdf, os.path.join(DOCS, "thumb")], check=True)
        src = os.path.join(DOCS, f"thumb-{p:02d}.png")
        if not os.path.exists(src):
            src = os.path.join(DOCS, f"thumb-{p}.png")
        dst = os.path.join(DOCS, f"page{p}.png")
        os.rename(src, dst)
        tags.append(f'<img src="page{p}.png" alt="guide page {p}" loading="lazy">')
    open(os.path.join(DOCS, "index.html"), "w").write(
        PAGE.replace("%%", "\x00") % {"demo": DEMO, "thumbs": "".join(tags), "v": VERSION}
    )
    fixed = open(os.path.join(DOCS, "index.html")).read().replace("\x00", "%")
    open(os.path.join(DOCS, "index.html"), "w").write(fixed)
    open(os.path.join(DOCS, "version.txt"), "w").write(VERSION + "\n")
    open(os.path.join(DOCS, ".nojekyll"), "w").write("")
    sizes = sum(os.path.getsize(os.path.join(DOCS, f)) for f in os.listdir(DOCS))
    print(f"docs/ built, v{VERSION}, {sizes} bytes total")


if __name__ == "__main__":
    main()
