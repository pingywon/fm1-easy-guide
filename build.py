#!/usr/bin/env python3
import glob, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "fm1-easy-guide.html")
PDF = os.path.join(HERE, "FM-1-Easy-Guide.pdf")

VERSION = open(os.path.join(HERE, "VERSION")).read().strip()

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>FM-1 Easy Guide</title>
<link rel="stylesheet" href="fm1.css">
<style>@page {{ @bottom-center {{ content: "FM-1 Easy Guide · v{v} · page " counter(page); font-family: "Atkinson Hyperlegible", sans-serif; font-size: 8.5pt; color: #6b6b6b; }} }}</style>
</head><body>
""".format(v=VERSION)


BLACK_AFTER = [0, 1, 2, 4, 5, 7, 8, 9, 11, 12, 14]
TOP_LABELS = ["OP1", "OP2", "OP3", "OP4", "OP5", "OP6", "PIT", "GLO", "MONO", "POLY", ""]


def kbd(spec):
    """Two rows of pill keys like the real FM-1. Marks: 'N=label' bottom key N (1-16),
    'bN=label' the top key just right of bottom key N. A leading '!' = solid black."""
    marks, bmarks = {}, {}
    for item in filter(None, (s.strip() for s in spec.split(","))):
        k, _, lab = item.partition("=")
        (bmarks if k.startswith("b") else marks)[int(k.lstrip("b"))] = lab
    pitch, bw, bh, tw, th = 36, 30, 64, 28, 46
    W = 16 * pitch
    ytop_lab, ytop, ytop_txt, ybot = 18, 26, 26 + th + 13, 26 + th + 24
    ynum = ybot + bh + 15
    ymark = ynum + 17
    H = (ymark + 4) if any(marks.values()) else (ynum + 5)
    out = [f'<svg viewBox="-4 0 {W + 8} {H}" style="width:100%" aria-hidden="true">']

    def style(lab):
        if lab is None:
            return "#fff", "#111"
        return ("#111", "#fff") if lab.startswith("!") else ("#bdbdbd", "#111")

    for idx, after in enumerate(BLACK_AFTER):
        n = after + 1
        cx = n * pitch - 3
        lab = bmarks.get(n)
        fill, led = style(lab)
        out.append(f'<rect x="{cx - tw/2}" y="{ytop}" width="{tw}" height="{th}" rx="{tw/2}" fill="{fill}" stroke="#111" stroke-width="2"/>')
        out.append(f'<rect x="{cx - 2}" y="{ytop + 11}" width="4" height="{th - 22}" rx="2" fill="{led}" opacity="0.55"/>')
        if TOP_LABELS[idx]:
            out.append(f'<text x="{cx}" y="{ytop_txt}" text-anchor="middle" font-size="9.5" fill="#3a3a3a">{TOP_LABELS[idx]}</text>')
        if lab:
            out.append(f'<text x="{cx}" y="{ytop_lab - 3}" text-anchor="middle" font-size="12.5" class="f">{lab.lstrip("!")}</text>')
    for i in range(16):
        n = i + 1
        cx = i * pitch + pitch / 2 - 3
        lab = marks.get(n)
        fill, led = style(lab)
        out.append(f'<rect x="{cx - bw/2}" y="{ybot}" width="{bw}" height="{bh}" rx="{bw/2}" fill="{fill}" stroke="#111" stroke-width="2"/>')
        out.append(f'<rect x="{cx - 2}" y="{ybot + 13}" width="4" height="{bh - 26}" rx="2" fill="{led}" opacity="0.55"/>')
        out.append(f'<text x="{cx}" y="{ynum}" text-anchor="middle" font-size="13" class="f">{n}</text>')
        if lab:
            tx, anc = (cx - bw / 2, "start") if n == 1 else ((cx + bw / 2, "end") if n == 16 else (cx, "middle"))
            out.append(f'<text x="{tx}" y="{ymark}" text-anchor="{anc}" font-size="12" class="f">{lab.lstrip("!")}</text>')
    out.append("</svg>")
    return "".join(out)


def device(mode):
    numbered = mode.strip() == "numbers"
    demo = mode.strip() == "demo"
    o = ['<svg viewBox="0 0 760 450" style="width:100%"' + ('' if demo else ' aria-hidden="true"') + '>',
         '<rect x="2" y="2" width="756" height="446" rx="32" fill="#fff" stroke="#111" stroke-width="4"/>']
    badges = []

    def W(cid, s):
        return f'<g id="{cid}" class="ctl" data-ctl="{cid}">{s}</g>' if demo else s

    def badge(x, y, n):
        if numbered:
            badges.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#111" stroke="#fff" stroke-width="2"/>'
                          f'<text x="{x}" y="{y + 4.5}" text-anchor="middle" font-size="12.5" class="f" fill="#fff">{n}</text>')

    def knob(x, y, label, n=None, r=18, cid=None):
        ptr = f' id="{cid}-ptr" style="transform-origin:{x}px {y}px"' if demo else ''
        o.append(W(cid, f'<text x="{x}" y="{y - 27}" text-anchor="middle" font-size="12" class="f">{label}</text>'
                 f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e2e2e2" stroke="#111" stroke-width="3"/>'
                 f'<line{ptr} x1="{x}" y1="{y}" x2="{x}" y2="{y - r + 4}" stroke="#111" stroke-width="3" stroke-linecap="round"/>'))
        if n is not None:
            badge(x + r + 4, y - r + 2, n)

    knob(70, 72, "MASTER", 1, cid="ctl-master"); knob(152, 72, "SELECT", 2, cid="ctl-select")
    knob(70, 152, "PRESETS", 3, cid="ctl-presets"); knob(152, 152, "ALGORITHM", 4, cid="ctl-algorithm")
    o.append('<rect x="36" y="192" width="152" height="40" rx="10" fill="none" stroke="#111" stroke-width="2"/>')
    for x, t, cid in ((74, "OCT\u2212", "btn-octdown"), (150, "OCT+", "btn-octup")):
        o.append(W(cid, f'<rect x="{x - 28}" y="200" width="56" height="24" rx="6" fill="#fff" stroke="#111" stroke-width="2.5"/>'
                 f'<text x="{x}" y="216.5" text-anchor="middle" font-size="12" class="f">{t}</text>'))
    badge(194, 194, 5)
    if demo:
        o.append('<rect x="212" y="30" width="176" height="200" rx="20" fill="#111"/>'
                 '<rect x="226" y="46" width="148" height="160" rx="6" fill="#fff"/>'
                 '<text id="scr-top" x="236" y="66" font-size="12" class="f">001 PIANO 1</text>'
                 '<path id="scr-wave" d="M236 130 C 256 90, 272 90, 290 130 S 322 170, 340 130 S 358 104, 366 118" fill="none" stroke="#111" stroke-width="3"/>'
                 '<text id="scr-mid" x="300" y="128" text-anchor="middle" font-size="15" class="f"></text>'
                 '<text id="scr-mid2" x="300" y="150" text-anchor="middle" font-size="11"></text>'
                 '<rect x="236" y="182" width="128" height="16" rx="3" fill="#e2e2e2"/>'
                 '<text id="scr-bot" x="240" y="194" font-size="10" class="f"></text>')
    else:
        o.append('<rect x="212" y="30" width="176" height="200" rx="20" fill="#111"/>'
                 '<rect x="226" y="46" width="148" height="160" rx="6" fill="#fff"/>'
                 '<text x="236" y="66" font-size="12" class="f">001 PIANO 1</text>'
                 '<path d="M236 130 C 256 90, 272 90, 290 130 S 322 170, 340 130 S 358 104, 366 118" fill="none" stroke="#111" stroke-width="3"/>'
                 '<rect x="236" y="182" width="128" height="16" rx="3" fill="#e2e2e2"/>')
    badge(392, 36, 6)
    for k in range(4):
        knob(448 + k * 88, 72, f"KNOB{k + 1}", r=17, cid=f"ctl-knob{k + 1}")
    badge(448 + 3 * 88 + 30, 96, 7)
    o.append('<rect x="414" y="116" width="324" height="116" rx="14" fill="none" stroke="#111" stroke-width="2"/>')
    rows = [["FX", "SEL", "ENV", "LFO", "EDIT", "GLO"], ["HOME", "SAVE", "ARP", "SEQ", "PLAY/STOP", "REC"]]
    bid = {"FX": "btn-fx", "SEL": "btn-sel", "ENV": "btn-env", "LFO": "btn-lfo", "EDIT": "btn-edit", "GLO": "btn-glo",
           "HOME": "btn-home", "SAVE": "btn-save", "ARP": "btn-arp", "SEQ": "btn-seq", "PLAY/STOP": "btn-play", "REC": "btn-rec"}
    for r, row in enumerate(rows):
        for c, t in enumerate(row):
            x = 428 + c * 51.5
            y = 128 + r * 50
            b = f'<rect x="{x}" y="{y}" width="44" height="38" rx="7" fill="#fff" stroke="#111" stroke-width="2.5"/>'
            if t == "PLAY/STOP":
                b += (f'<text x="{x + 22}" y="{y + 17}" text-anchor="middle" font-size="9.5" class="f">PLAY</text>'
                      f'<text x="{x + 22}" y="{y + 29}" text-anchor="middle" font-size="9.5" class="f">STOP</text>')
            else:
                b += f'<text x="{x + 22}" y="{y + 23.5}" text-anchor="middle" font-size="{11 if len(t) < 4 else 10}" class="f">{t}</text>'
            if demo:
                b += f'<circle id="{bid[t]}-led" class="led" cx="{x + 37}" cy="{y + 6.5}" r="3.2" fill="#fff" stroke="#111" stroke-width="1.2"/>'
            o.append(W(bid[t], b))
            badge(x + 4, y + 2, 8 + r * 6 + c)
    o.append('<rect x="26" y="252" width="708" height="180" rx="26" fill="#111"/>')
    top = ["OP1", "OP2", "OP3", "OP4", "OP5", "OP6", "PIT", "GLO", "MONO", "POLY", ""]
    after = [0, 1, 2, 4, 5, 7, 8, 9, 11, 12, 14]
    for idx, a in enumerate(after):
        cx = 59 + (a + 0.5) * 43.2
        t = (f'<rect x="{cx - 15}" y="266" width="30" height="54" rx="15" fill="#fff" stroke="#111" stroke-width="2"/>'
             f'<rect x="{cx - 2}" y="278" width="4" height="30" rx="2" fill="#9a9a9a"/>')
        if top[idx]:
            t += f'<text x="{cx}" y="336" text-anchor="middle" font-size="9.5" fill="#fff">{top[idx]}</text>'
        o.append(W(f"key-t{idx + 1}", t))
    for i in range(16):
        cx = 59 + i * 43.2
        n = i + 1
        k = (f'<rect x="{cx - 18}" y="346" width="36" height="72" rx="18" fill="#fff" stroke="#111" stroke-width="2"/>'
             f'<rect id="kled-{n}" x="{cx - 2}" y="358" width="4" height="{26 if (numbered or demo) else 48}" rx="2" fill="#9a9a9a"/>') if demo else (
            f'<rect x="{cx - 18}" y="346" width="36" height="72" rx="18" fill="#fff" stroke="#111" stroke-width="2"/>'
            f'<rect x="{cx - 2}" y="358" width="4" height="{26 if numbered else 48}" rx="2" fill="#9a9a9a"/>')
        if numbered or demo:
            k += f'<text x="{cx}" y="409" text-anchor="middle" font-size="13" class="f">{n}</text>'
        o.append(W(f"key-b{n}", k))
    badge(30, 262, 20)
    o.extend(badges)
    o.append("</svg>")
    return "".join(o)


def beat(spec):
    """16 or 8 tokens. B/S/t = boom/snap/tick, '.' = rest, other = key number or label.
    Options: '@8' count in eighths (1 & 2 & ...), '@keys' add a what-to-press row (B=1, S=9, t=16)."""
    toks = spec.split()
    opts = {t for t in toks if t.startswith("@")}
    toks = [t for t in toks if not t.startswith("@")]
    n = len(toks)
    assert n in (8, 16), spec
    eighths = "@8" in opts
    grid = f' style="grid-template-columns: repeat({n}, 1fr)"'
    counts = []
    for i in range(n):
        if eighths:
            counts.append(f'<div class="on">{(i // 2) % 4 + 1}</div>' if i % 2 == 0 else "<div>&amp;</div>")
        else:
            counts.append(f'<div class="on">{i // 4 + 1}</div>' if i % 4 == 0 else "<div>·</div>")
    cells = []
    for t in toks:
        if t == "B":
            cells.append('<div class="B">B</div>')
        elif t == "S":
            cells.append('<div class="S"><span>S</span></div>')
        elif t == "t":
            cells.append('<div class="t">t</div>')
        elif t == ".":
            cells.append('<div class="r"></div>')
        else:
            cells.append(f'<div class="n">{t}</div>')
    out = [f'<div class="beat{" eight" if n == 8 else ""}"><div class="counts"{grid}>{"".join(counts)}</div>',
           f'<div class="cells"{grid}>{"".join(cells)}</div>',
           f'<div class="stepno"{grid}>' + "".join(f"<div>step {i}</div>" if n == 8 else f"<div>{i}</div>" for i in range(1, n + 1)) + "</div>"]
    if "@keys" in opts:
        keymap = {"B": "1", "S": "9", "t": "16", ".": "gap"}
        press = "".join(f'<div class="{"gap" if keymap.get(t, t) == "gap" else "k"}">{keymap.get(t, t) if t != "." else "gap"}</div>' for t in toks)
        out.append(f'<div class="press"{grid}>{press}</div>')
    out.append("</div>")
    return "".join(out)


def assemble(pages):
    body = "\n".join(open(p).read() for p in sorted(glob.glob(os.path.join(HERE, "parts", "*.html"))))
    body = re.sub(r"<!--KBD:([^>]*)-->", lambda m: kbd(m.group(1)), body)
    body = re.sub(r"<!--BEAT:([^>]*)-->", lambda m: beat(m.group(1)), body)
    body = re.sub(r"<!--DEVICE:([^>]*)-->", lambda m: device(m.group(1)), body)
    body = body.replace("{{VERSION}}", VERSION)
    def fill(m):
        key = m.group(1)
        return f'<span class="pg" data-for="{key}">{pages.get(key, "")}</span>'
    body = re.sub(r'<span class="pg" data-for="([\w-]+)">[^<]*</span>', fill, body)
    open(HTML, "w").write(HEAD + body + "\n</body></html>\n")
    return body


def render():
    subprocess.run([
        "chromium", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
        "--virtual-time-budget=4000", f"--print-to-pdf={PDF}", "file://" + HTML,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def page_texts():
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", PDF], capture_output=True, text=True).stdout).group(1))
    out = []
    for i in range(1, n + 1):
        t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), PDF, "-"], capture_output=True, text=True).stdout
        out.append(re.sub(r"\s+", " ", t))
    return out


def toc_targets(body):
    found = {}
    for m in re.finditer(r'<h[1-4][^>]*data-toc="([\w-]+)"[^>]*>(.*?)</h[1-4]>', body, re.S):
        text = re.sub(r"<[^>]+>", " ", m.group(2))
        text = re.sub(r"\s+", " ", text.replace("&amp;", "&")).strip()
        found[m.group(1)] = text
    return found


def main():
    body = assemble({})
    render()
    targets = toc_targets(body)
    texts = page_texts()
    pages = {}
    for key, label in targets.items():
        probe = label[:40]
        hits = [i for i, t in enumerate(texts, 1)
                if i > 1 and probe in t and "What's inside" not in t and "What’s inside" not in t]
        top = [i for i in hits if probe in texts[i - 1][:90]]
        if top or hits:
            pages[key] = (top or hits)[0]
        else:
            print(f"WARN: heading not found in PDF: {key!r} {probe!r}", file=sys.stderr)
    wanted = set(re.findall(r'data-for="([\w-]+)"', body))
    for k in sorted(wanted - set(pages)):
        print(f"WARN: no page for {k}", file=sys.stderr)
    assemble(pages)
    render()
    print(f"{PDF}: {len(page_texts())} pages")


if __name__ == "__main__":
    main()
