#!/usr/bin/env python3
"""Builds demo/site/ (the Follow-Along app) from demo/src/app.html."""
import os, shutil, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import build  # the guide's own generator; device("demo") draws the clickable panel

PAGES = "https://pingywon.github.io/fm1-easy-guide/"
VERSION = open(os.path.join(HERE, "VERSION")).read().strip()
SITE = os.path.join(HERE, "demo", "site")


def main():
    shutil.rmtree(SITE, ignore_errors=True)
    os.makedirs(os.path.join(SITE, "fonts"))
    html = open(os.path.join(HERE, "demo", "src", "app.html")).read()
    for k, v in (("{{PANEL}}", build.device("demo")), ("{{VERSION}}", VERSION), ("{{PAGES}}", PAGES)):
        assert k in html, k
        html = html.replace(k, v)
    open(os.path.join(SITE, "index.html"), "w").write(html)
    for f in os.listdir(os.path.join(HERE, "fonts")):
        if f.endswith(".woff2"):
            shutil.copy(os.path.join(HERE, "fonts", f), os.path.join(SITE, "fonts", f))
    open(os.path.join(SITE, "_headers"), "w").write(
        "/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-cache\n  X-Content-Type-Options: nosniff\n")
    open(os.path.join(SITE, "version.txt"), "w").write(VERSION + "\n")
    print(f"demo/site built, v{VERSION}, {len(html)} bytes")


if __name__ == "__main__":
    main()
