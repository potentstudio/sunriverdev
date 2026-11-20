#!/usr/bin/env python3
"""One-time compression pass over the raster images committed to the repo (media/ and assets/img/).

Run it by hand and commit the results. It is NOT part of the build.

    python3 tools/compress_media.py            # rewrite files in place, print a before/after table
    python3 tools/compress_media.py --dry-run  # only report what would change

What it does
  * Works from what a file really contains, not its extension. Most files in media/v were copied from the old
    dev site as WebP data under .jpg and .png names; many of those are lossless WebP, which is why a 1500 px
    photo could weigh 2 MB.
  * WebP stays WebP (quality 80). JPEG stays JPEG (progressive, quality 80). A photo saved as PNG under a .jpg
    name becomes a real JPEG. The filename never changes, so no page needs editing.
  * The longest edge is capped at 2400 px, aspect ratio unchanged.
  * A file is left alone when it is already small (under 150 KB and either already lossy or a graphic with
    transparency), or when the new version would not be at least 10% smaller.
  * Nothing ends above 400 KB: if quality 80 at 2400 px is not enough, it steps the quality down to 70, then
    the longest edge down to 2000 and 1600.
  * A large opaque PNG under a .png name is a photo too. It becomes WebP data under the same name, which is
    what its neighbours in media/v already are (browsers and Vercel go by the content, not the extension).
  * SVGs, logos, icons, badges and wordmarks are never touched. PNG graphics (transparency, or under 150 KB)
    are only re-saved losslessly.
"""
import io
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FOLDERS = ("media", "assets/img")
MAX_EDGE = 2400
QUALITY = 80
LIMIT = 400 * 1024          # no raster image may end above this
SMALL = 150 * 1024          # lossy files under this are left as they are
MIN_GAIN = 0.10             # keep the original unless the new file is at least 10% smaller
SKIP = re.compile(r"(logo|icon|badge|wordmark|favicon)", re.I)
RASTER = (".jpg", ".jpeg", ".png", ".webp")


def is_lossless_webp(data):
    """A WebP file is lossless when its first image chunk is VP8L (possibly after a VP8X header)."""
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return False
    pos = 12
    while pos + 8 <= len(data):
        tag = data[pos:pos + 4]
        size = int.from_bytes(data[pos + 4:pos + 8], "little")
        if tag == b"VP8L":
            return True
        if tag == b"VP8 ":
            return False
        pos += 8 + size + (size & 1)
    return False


def has_transparency(im):
    if im.mode not in ("RGBA", "LA", "P"):
        return False
    return im.convert("RGBA").getchannel("A").getextrema()[0] < 255


def encode(im, fmt, quality):
    buf = io.BytesIO()
    if fmt == "JPEG":
        im.convert("RGB").save(buf, "JPEG", quality=quality, progressive=True, optimize=True)
    elif fmt == "WEBP":
        im.save(buf, "WEBP", quality=quality, method=6)
    else:
        im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def plan(path):
    """Returns (new bytes or None, note)."""
    data = path.read_bytes()
    im = Image.open(io.BytesIO(data))
    if getattr(im, "is_animated", False):
        return None, "animated, skipped"
    real = im.format
    lossless_source = real == "PNG" or (real == "WEBP" and is_lossless_webp(data))
    im = ImageOps.exif_transpose(im)
    alpha = has_transparency(im)
    oversize = max(im.size) > MAX_EDGE
    if not lossless_source and len(data) < SMALL and not oversize:
        return None, "already small"
    if alpha and len(data) < SMALL and not oversize:
        return None, "small graphic with transparency"

    ext = path.suffix.lower()
    if real == "PNG" and ext == ".png":
        # A real PNG. Graphics (transparency, or small) are only re-saved losslessly. A large opaque one is a
        # photo: it becomes WebP data under the same name, like the other photos already in this folder.
        target = "PNG" if (alpha or len(data) < SMALL) else "WEBP"
    elif real == "PNG":
        target = "PNG" if alpha else "JPEG"  # a photo saved as PNG under a .jpg name
    elif real == "JPEG":
        target = "JPEG"
    else:
        target = "WEBP"

    if target != "PNG":
        im = im.convert("RGBA" if alpha else "RGB")
    # Quality 80 at up to 2400 px first. Only a file that is still over the limit moves down this ladder.
    for quality, edge in ((QUALITY, MAX_EDGE), (75, MAX_EDGE), (70, MAX_EDGE), (75, 2000), (70, 2000), (70, 1600)):
        work = im
        if max(work.size) > edge:
            scale = edge / float(max(work.size))
            work = work.resize((max(1, round(work.width * scale)), max(1, round(work.height * scale))), Image.LANCZOS)
        out = encode(work, target, quality)
        if len(out) <= LIMIT or target == "PNG":
            break
    if len(out) > len(data) * (1 - MIN_GAIN) and not oversize:
        return None, "no real gain"
    note = "%s to %s q%d" % ("lossless " + real if lossless_source else real, target, quality) if target != "PNG" else "PNG re-saved"
    if work.size != im.size:
        note += ", %dx%d to %dx%d" % (im.width, im.height, work.width, work.height)
    return out, note


def main():
    dry = "--dry-run" in sys.argv
    rows, before_total, after_total = [], 0, 0
    for folder in FOLDERS:
        for path in sorted((ROOT / folder).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in RASTER:
                continue
            size = path.stat().st_size
            before_total += size
            rel = path.relative_to(ROOT).as_posix()
            if SKIP.search(rel):
                after_total += size
                continue
            out, note = plan(path)
            if out is None:
                after_total += size
                continue
            if not dry:
                path.write_bytes(out)
            after_total += len(out)
            rows.append((size, len(out), rel, note))
    rows.sort(reverse=True)
    print("| File | Before | After | Saved | What changed |")
    print("|---|---:|---:|---:|---|")
    for size, new, rel, note in rows:
        print("| `%s` | %d KB | %d KB | %d%% | %s |" % (rel, size // 1024, new // 1024, round(100 * (1 - new / size)), note))
    print()
    print("%d files rewritten%s. Raster total: %.1f MB to %.1f MB." % (len(rows), " (dry run)" if dry else "", before_total / 1e6, after_total / 1e6))
    over = [p for folder in FOLDERS for p in (ROOT / folder).rglob("*") if p.is_file() and p.suffix.lower() in RASTER and p.stat().st_size > LIMIT]
    if not dry:
        print("Raster files still over %d KB: %d %s" % (LIMIT // 1024, len(over), [p.name for p in over]))


if __name__ == "__main__":
    main()
