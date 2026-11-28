"""Download any new videos listed in the website feed (daily results, free pick of the day, free pick results),
keep the newest 14 of each kind, and write feed.xml pointing at this repo."""
import os, re, urllib.request, xml.etree.ElementTree as ET

SITE_FEED = "https://computerprediction.com/videos/feed.xml"
RAW = "https://raw.githubusercontent.com/sbredrock-cpu/cp-videos/main/"
KEEP = 14
PAT = r"CP-(Results|FreePick|FPResults)-\d{4}-\d{2}-\d{2}\.mp4"
UA = {"User-Agent": "cp-video-mirror"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


root = ET.fromstring(get(SITE_FEED))
channel = root.find("channel")
items = channel.findall("item")
for it in items:
    enc = it.find("enclosure")
    if enc is None:
        continue
    name = os.path.basename(enc.get("url"))
    if not re.fullmatch(PAT, name):
        continue
    if not os.path.exists(name):
        data = get(enc.get("url"))
        if data[4:8] != b"ftyp":
            raise SystemExit(f"{name}: not an MP4 (got {len(data)} bytes)")
        open(name, "wb").write(data)
        print("copied", name, len(data))
    enc.set("url", RAW + name)
    enc.set("length", str(os.path.getsize(name)))

vids = [f for f in os.listdir(".") if re.fullmatch(PAT, f)]
keep = [f for k in ("Results", "FreePick", "FPResults") for f in sorted(v for v in vids if v.startswith(f"CP-{k}-"))[-KEEP:]]
for f in vids:
    if f not in keep:
        os.remove(f)
for it in items:
    enc = it.find("enclosure")
    if enc is not None and os.path.basename(enc.get("url")) not in keep:
        channel.remove(it)
ET.ElementTree(root).write("feed.xml", encoding="UTF-8", xml_declaration=True)
print("feed.xml:", len(channel.findall("item")), "items")
