"""Shared building blocks for the SunRiver static site.

Pages are rendered into the PAGES dict ({url path: html}) and written by build.py.
Image helpers:
  V(name)   a file from the dev site's /_next/static/media folder (mirrored into /media/v at build time)
  VP(path)  any other public file on the dev site, e.g. /images/icons/bed.png (also mirrored)
  S(ref)    a Sanity CMS image, hotlinked from cdn.sanity.io
  SQ(path)  an image on the current sunriver.com Squarespace CDN
"""
import hashlib
import html
import os
import re
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timedelta

VERCEL = "https://sunriver-website.vercel.app"
SANITY_CDN = "https://cdn.sanity.io/images/ib6s13lu/production/"
SQUARESPACE = "https://images.squarespace-cdn.com/content/v1/65e0b11913912d2c2162c71b/"
SITE_NAME = "SunRiver Firelight"
PHONE = "(435) 688-1000"
PHONE_TEL = "tel:+14356881000"

# HubSpot forms (portal 242537243, region na2). These are the same forms the Squarespace sunriver.com embeds, so a
# lead from this site lands in the same form, list and workflow as before. site.js posts to HubSpot's submission API.
HS_FORMS = {
    "general": "3e5cb955-84b0-49f6-96a9-1efde323356e",        # "What are you interested in?" (sunriver.com/find-a-home)
    "founders": "608c7cfe-99ed-4e03-9841-52929941eb61",       # same fields, Founders Club page
    "contact": "f997128f-2c56-417b-932d-cc803fc781a8",        # Contact page (phone required, text consent, lead source)
    "villas": "e131ea33-9c06-4fc3-982a-3691be90369f",         # Discovery Villas stay request
    "villas-meta": "c7814775-6e25-4a6b-bc6d-6c66654fbcb1",    # Discovery Villas landing page for Meta ads
    "firelight-bing": "1392ee00-fac4-421e-bde8-f6e44b4497b7", # SunRiver Firelight landing page for Microsoft ads
}
# Thank-you lines, copied from each HubSpot form's own confirmation message
HS_THANKS = {
    "general": "Thank you! One of our SunRiver professionals will be in touch shortly.",
    "founders": "Thank you, we'll be in touch soon.",
    "contact": "Thank you, we'll be in touch soon.",
    "villas": "A member of the SunRiver team will be in touch shortly to finalize details and confirm availability of your requested date!",
    "villas-meta": "A member of the SunRiver team will be in touch shortly to finalize details and confirm availability of your requested date!",
    "firelight-bing": "Thank you! A SunRiver agent will send current availability and pricing within one business day.",
}
# Conversions HubSpot's ads integration fires for these forms on sunriver.com (read from the portal's public
# pixel config). site.js fires the same ones after a successful submission.
HS_ADS = {
    "contact": ' data-ads-conv="AW-988674249/0ZvlCPfP--wcEMnxt9cD" data-fb-lead',
    "villas-meta": " data-fb-lead",
}
# Interest options: the label shown, and the exact option value stored on the HubSpot contact property
HS_INTERESTS = [
    ("Speak With A SunRiver Agent", "Speak With A SunRiver Agent"),
    ("Availability Info", "Availability Info"),
    ("Learn More About SunRiver Firelight", "Learn More About Firelight"),
    ("Financing Options", "Financing Options"),
    ("Something Else", "Something Else"),
]


def hs_attrs(key):
    """Attributes that connect a <form> to its HubSpot form (see the Forms block in site.js)."""
    return 'data-hs-form="%s" data-hs-key="%s" data-hs-thanks="%s"%s' % (HS_FORMS[key], key, html.escape(HS_THANKS[key], quote=True), HS_ADS.get(key, ""))


# Left blank by people, filled in by bots: site.js quietly drops any submission where this has a value
HONEYPOT = '<div class="hp-field" aria-hidden="true"><label>Leave this field empty<input type="text" name="company_website" tabindex="-1" autocomplete="off"></label></div>'

# Analytics and ad tags, the same set sunriver.com runs today: Google Tag Manager, Google Ads, Google Analytics,
# HubSpot, Microsoft Ads and the Meta pixel. They load on the real domain only, so preview and test builds
# (vercel.app, localhost) never show up in the numbers. To test on another host, run
# localStorage.setItem("sr_track", "1") in the browser console and reload.
TRACKING = '''<script>
(function () {
  var live = /(^|\\.)sunriver\\.com$/.test(location.hostname), forced = false;
  try { forced = localStorage.getItem("sr_track") === "1"; } catch (e) {}
  if (!live && !forced) return;
  function load(src, id) { var s = document.createElement("script"); s.async = true; s.src = src; if (id) s.id = id; document.head.appendChild(s); }
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { dataLayer.push(arguments); };
  // Google Tag Manager
  dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
  load("https://www.googletagmanager.com/gtm.js?id=GTM-TLZP4TZ5");
  // Google Ads and Google Analytics
  gtag("js", new Date());
  gtag("config", "AW-988674249");
  gtag("config", "G-GB768NFV7L");
  load("https://www.googletagmanager.com/gtag/js?id=G-GB768NFV7L");
  // HubSpot tracking code (also what shows HubSpot pop-ups and the cookie banner)
  load("https://js-na2.hs-scripts.com/242537243.js", "hs-script-loader");
  // Microsoft Ads
  (function (w, d, t, r, u) { var f, n, i; w[u] = w[u] || []; f = function () { var o = { ti: "295031258" }; o.q = w[u]; w[u] = new UET(o); w[u].push("pageLoad"); };
    n = d.createElement(t); n.src = r; n.async = 1; n.onload = n.onreadystatechange = function () { var s = this.readyState; if (s && s !== "loaded" && s !== "complete") return; f(); n.onload = n.onreadystatechange = null; };
    i = d.getElementsByTagName(t)[0]; i.parentNode.insertBefore(n, i); })(window, document, "script", "https://bat.bing.com/bat.js", "uetq");
  // Meta pixel
  !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
    if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t, s); }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
  fbq("init", "1500752294168842");
  fbq("track", "PageView");
})();
</script>'''

MIRROR = {}   # local path -> remote url
_ASSETS = Path(__file__).resolve().parent.parent / "assets"


def asset_v(name):
    """Content hash for cache busting, so browsers pick up new CSS and JS right after a deploy."""
    return hashlib.md5((_ASSETS / name).read_bytes()).hexdigest()[:10]

PAGES = {}    # url path ("/", "/about", ...) -> html


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def clean(s):
    """Brand rule: no em dashes anywhere in published copy (CMS text included)."""
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"\s*—\s*", " - ", s)
    return s


def mirror(remote_path):
    local = "/media/v/" + remote_path.lstrip("/").replace("_next/static/media/", "")
    MIRROR[local] = VERCEL + remote_path
    return local


def V(name):
    return mirror("/_next/static/media/" + name)


def VP(path):
    return mirror(path)


def SQ(path):
    return SQUARESPACE + path


def sanity_id(ref):
    """'image-<hash>-WxH-ext' or '<hash>-WxH.ext' -> ('<hash>-WxH.ext', W, H)."""
    r = ref[6:] if ref.startswith("image-") else ref
    if "." not in r:
        base, ext = r.rsplit("-", 1)
        r = base + "." + ext
    m = re.search(r"-(\d+)x(\d+)\.", r)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    return r, w, h


def S(ref, w=None):
    if ref.startswith("http"):  # an outside image (MLS photos): used as is
        return ref
    if ref.startswith("/"):  # a photo kept in this repo (homesite photos): small sizes use its -t thumbnail
        return ref[:-5] + "-t.webp" if w and w <= 640 and ref.endswith(".webp") else ref
    fid, ow, _ = sanity_id(ref)
    url = SANITY_CDN + fid
    if fid.endswith(".svg"):
        return url
    q = ["auto=format", "fit=max", "q=80"]
    if w:
        q.append("w=%d" % min(w, ow or w))
    return url + "?" + "&".join(q)


# ------------------------------------------------------------------ local images
# Local raster images (/media/... and /assets/img/...) get three things from img():
#   * width and height, read from the file, so the page does not jump while images load
#   * a ?v=<content hash> on the plain URL, so a replaced file is fetched again (media is cached for a year)
#   * on Vercel, a srcset through Vercel Image Optimization (/_vercel/image), so a phone downloads a
#     phone-size AVIF or WebP instead of the full file. The widths and quality must be listed under "images"
#     in vercel.json, or the service answers with an error.
# Off Vercel (local preview, Netlify) the plain file is used, so nothing depends on the service.
_REPO = Path(__file__).resolve().parent.parent
ON_VERCEL = os.environ.get("VERCEL") == "1"
IMG_WIDTHS = (640, 1080, 1600, 2400)   # keep in step with images.sizes in vercel.json
IMG_QUALITY = 75                       # keep in step with images.qualities in vercel.json
_RASTER = (".jpg", ".jpeg", ".png", ".webp")
_IMG_INFO = {}


def local_image(src):
    """The file in this repo behind a local raster image URL, or None (remote images, SVGs, files that are
    only mirrored in at build time)."""
    path = src.split("?", 1)[0].split("#", 1)[0]
    if not path.startswith(("/media/", "/assets/img/")) or not path.lower().endswith(_RASTER):
        return None
    candidates = [_REPO / path.lstrip("/")]
    if path.startswith("/media/fg/"):   # figma_assets lets a file in assets/fg override the one in media/fg
        candidates.insert(0, _REPO / "assets" / "fg" / path.rsplit("/", 1)[1])
    for f in candidates:
        if f.is_file():
            return f
    return None


def image_info(src):
    """(width, height, content hash) of a local raster image, cached. None when the file is not in the repo
    or Pillow is not installed."""
    path = src.split("?", 1)[0].split("#", 1)[0]
    if path not in _IMG_INFO:
        info, f = None, local_image(path)
        if f:
            try:
                from PIL import Image
                with Image.open(f) as im:
                    info = (im.width, im.height, hashlib.md5(f.read_bytes()).hexdigest()[:8])
            except Exception:  # noqa: BLE001  (no Pillow, or not an image: fall back to a plain <img>)
                info = None
        _IMG_INFO[path] = info
    return _IMG_INFO[path]


def other_size(src):
    """Pixel size for images that are not local rasters, where it can be known without downloading anything:
    a Sanity image carries its size in its filename, and a local SVG states it in its viewBox."""
    m = re.search(r"cdn\.sanity\.io/images/[^?]*-(\d+)x(\d+)\.\w+(\?.*)?$", src)
    if m:
        if m.group(3) and re.search(r"[?&](h=|rect=|crop=|fit=(?!max))", m.group(3)):   # cropped: not the file's shape
            return None
        return int(m.group(1)), int(m.group(2))
    path = src.split("?", 1)[0].split("#", 1)[0]
    if path.startswith(("/media/", "/assets/")) and path.lower().endswith(".svg"):
        if path not in _IMG_INFO:
            dims, f = None, _REPO / path.lstrip("/")
            if f.is_file():
                head = f.read_text(encoding="utf-8", errors="ignore")[:2000]
                vb = re.search(r'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', head)
                if vb and float(vb.group(1)) > 0 and float(vb.group(2)) > 0:
                    dims = (round(float(vb.group(1))), round(float(vb.group(2))))
            _IMG_INFO[path] = dims
        return _IMG_INFO[path]
    return None


def versioned(src):
    """src with ?v=<content hash> added, for a local raster image that has no query string yet."""
    info = image_info(src)
    return "%s?v=%s" % (src, info[2]) if info and "?" not in src else src


def image_srcset(src):
    """srcset for a local raster image through Vercel Image Optimization, or "" when it does not apply.
    Only widths up to the file's own are listed. When the file is wider than the largest of those (a 1500 px
    photo, say), one more entry asks for the next allowed width and is labelled with the file's real width:
    the service never enlarges, so that returns the full-size picture as AVIF or WebP."""
    info = image_info(src)
    if not ON_VERCEL or not info:
        return ""
    width = info[0]
    widths = [w for w in IMG_WIDTHS if w <= width]
    if not widths:
        return ""
    url = quote(src.split("?", 1)[0].split("#", 1)[0], safe="")
    # v is not read by the service. It is there because the resized image is sent with the same browser cache
    # lifetime as the file it came from (a year for /media/), so the URL has to change when the file does.
    entry = lambda w, label: "/_vercel/image?url=%s&amp;w=%d&amp;q=%d&amp;v=%s %dw" % (url, w, IMG_QUALITY, info[2], label)
    entries = [entry(w, w) for w in widths]
    if width > widths[-1]:
        larger = [w for w in IMG_WIDTHS if w > width]
        entries.append(entry(larger[0], width) if larger else "%s %dw" % (versioned(src), width))
    return ", ".join(entries)


def img(src, alt="", cls="", loading="lazy", attrs="", sizes="100vw", priority=False):
    """An <img>. sizes says how wide the image is shown (a CSS sizes value); it only matters for local images
    on Vercel, where it picks the right entry from the srcset. priority marks the page's main image (the hero):
    it loads first, ahead of everything else. A hero image (class fah-hero-img) is the main image by default."""
    c = ' class="%s"' % cls if cls else ""
    if priority or ("fah-hero-img" in cls and loading == "eager"):
        loading = "eager"
        if "fetchpriority" not in attrs:
            attrs = ('fetchpriority="high" ' + attrs).strip()
    extra = ""
    info = image_info(src)
    if info and "srcset=" not in attrs:
        srcset = image_srcset(src)
        if srcset:
            extra += ' srcset="%s" sizes="%s"' % (srcset, sizes)
        if "width=" not in attrs:
            extra += ' width="%d" height="%d"' % info[:2]
        src = versioned(src)
    elif "width=" not in attrs:
        dims = other_size(src)
        if dims:
            extra += ' width="%d" height="%d"' % dims
    a = (" " + attrs) if attrs else ""
    return '<img src="%s" alt="%s"%s loading="%s" decoding="async"%s%s>' % (src, esc(alt), c, loading, extra, a)


# How wide a local image is shown, by where it sits on the page: (class on the image or one of its three nearest
# ancestors, CSS sizes value). img() writes sizes="100vw" unless a caller passes something else; add() then
# swaps that default for the first match below, so a photo in a three-across grid is not sent the file a
# full-width hero needs. Full-width images (heroes, bands, banners, the footer photo) match nothing and stay
# at 100vw. The values come from measuring every page at 1440 px and 390 px wide. To set one by hand, pass
# sizes= to img(), photo() or simg(): an explicit value is never replaced.
_PHONE = "(max-width: 860px) "
IMG_SIZES = [
    ("thumb", _PHONE + "22vw, 14vw"),
    ("ht-node", _PHONE + "22vw, 12vw"),
    ("community-logo", _PHONE + "38vw, 11vw"), ("ws-comm-logo", _PHONE + "55vw, 17vw"), ("fh-badge", _PHONE + "30vw, 13vw"),
    ("day", _PHONE + "45vw, 17vw"),
    ("lon-t-paddle", _PHONE + "100vw, 46vw"), ("lon-tile", _PHONE + "45vw, 34vw"),
    ("dv2-col-small", _PHONE + "50vw, 18vw"),
    ("home-img", _PHONE + "100vw, 20vw"),
    ("lon-slide", _PHONE + "100vw, 75vw"), ("dz-pane", _PHONE + "100vw, 78vw"), ("team-photo", _PHONE + "100vw, 70vw"),
    ("viewer-main", _PHONE + "100vw, 55vw"), ("h4-couple", _PHONE + "100vw, 55vw"),
    ("wordmark", _PHONE + "80vw, 36vw"),
    ("photo-card", _PHONE + "100vw, 28vw"), ("person", _PHONE + "100vw, 28vw"), ("cols-2", _PHONE + "100vw, 28vw"),
    ("homes-trio", _PHONE + "100vw, 28vw"), ("lo-card", _PHONE + "100vw, 25vw"), ("fl-amen-img", _PHONE + "100vw, 25vw"),
    ("dv2-link-img", _PHONE + "100vw, 26vw"), ("badge-wrap", _PHONE + "75vw, 26vw"),
    ("hd-team", _PHONE + "100vw, 32vw"), ("fl-promo-img", _PHONE + "100vw, 34vw"), ("ws-comm-photo", _PHONE + "100vw, 32vw"),
    ("community-img", _PHONE + "100vw, 30vw"), ("fl-img", _PHONE + "100vw, 36vw"), ("lon-built-tile", _PHONE + "100vw, 35vw"),
    ("dv2-col-main", _PHONE + "100vw, 32vw"), ("hy-img", _PHONE + "100vw, 37vw"), ("lon-running-couple", _PHONE + "100vw, 37vw"),
    ("lo-visit-couple", _PHONE + "100vw, 48vw"), ("dv2-day-img", _PHONE + "100vw, 34vw"),
    ("lp-shot", _PHONE + "100vw, 43vw"), ("amen-row", _PHONE + "100vw, 41vw"), ("split", _PHONE + "100vw, 41vw"),
    ("dv2-split-img", _PHONE + "100vw, 41vw"), ("li-dc-img", _PHONE + "100vw, 42vw"), ("lp-dv-photo", _PHONE + "100vw, 41vw"),
    ("ws-map", _PHONE + "100vw, 41vw"),
    ("dv-dest-photo", _PHONE + "100vw, 28vw"),
]
_VOID = {"img", "br", "hr", "input", "source", "link", "meta", "area", "base", "col", "embed", "param", "track", "wbr"}
_TAG = re.compile(r"<(/?)([a-zA-Z][\w-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>")


def place_sizes(body):
    """Swap the default sizes="100vw" on optimized images for the value that fits where each image sits
    (see IMG_SIZES). Walks the markup once, keeping the classes of the open elements."""
    if 'sizes="100vw"' not in body or "/_vercel/image" not in body:
        return body
    out, stack, pos, skip_until = [], [], 0, None
    for m in _TAG.finditer(body):
        close, tag, rest = m.group(1), m.group(2).lower(), m.group(3)
        if skip_until:                       # inside <script> or <style>: not markup
            if close and tag == skip_until:
                skip_until = None
            continue
        if close:
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0] == tag:
                    del stack[k:]
                    break
            continue
        cls = re.search(r'\bclass="([^"]*)"', rest)
        cls = cls.group(1) if cls else ""
        if tag == "img":
            if ' sizes="100vw"' in rest and "/_vercel/image" in rest:
                where = " ".join([cls] + [c for _, c in stack[-3:]]).split()
                hit = next((v for k, v in IMG_SIZES if k in where), None)
                if hit:
                    out.append(body[pos:m.start()])
                    out.append(m.group(0).replace(' sizes="100vw"', ' sizes="%s"' % hit, 1))
                    pos = m.end()
            continue
        if tag in ("script", "style"):
            skip_until = tag
            continue
        if tag not in _VOID and not rest.rstrip().endswith("/"):
            stack.append((tag, cls))
    out.append(body[pos:])
    return "".join(out)


def deferred_img(src, alt=""):
    """An <img> that downloads nothing until site.js copies data-src into src (the photos in the Life at
    SunRiver menu, which is closed on most visits)."""
    info = image_info(src)
    dims = ' width="%d" height="%d"' % info[:2] if info else ""
    return '<img data-src="%s" alt="%s"%s decoding="async">' % (versioned(src), esc(alt), dims)


def preload_link(body):
    """<link rel="preload"> for the page's main image (the first one marked fetchpriority="high"), so the
    browser starts on it before it has read the rest of the page."""
    m = re.search(r'<img\b[^>]*\bfetchpriority="high"[^>]*>', body)
    if not m:
        return ""
    get = lambda tag, k: (re.search(r'\b%s="([^"]*)"' % k, tag) or [None, ""])[1]
    def link(tag, src_key, media=""):
        href, srcset, sizes = get(tag, src_key) if src_key == "src" else "", get(tag, "srcset"), get(tag, "sizes")
        if not href and not srcset:
            return ""
        out = '<link rel="preload" as="image" fetchpriority="high"'
        if href:
            out += ' href="%s"' % href
        if srcset:
            out += ' imagesrcset="%s" imagesizes="%s"' % (srcset, sizes or "100vw")
        return out + (' media="%s"' % media if media else "") + ">"
    tag = m.group(0)
    # inside a <picture> with one media-specific <source> (the homepage hero): one link per version
    before = body[max(0, m.start() - 600):m.start()]
    pic = before.rfind("<picture")
    if pic > -1 and "</picture>" not in before[pic:]:
        sources = re.findall(r"<source\b[^>]*>", before[pic:])
        if len(sources) == 1 and get(sources[0], "media"):
            media = get(sources[0], "media")
            return link(sources[0], "srcset", media) + "\n" + link(tag, "src", "not all and %s" % media)
        return ""
    return link(tag, "src")


def simg(ref, alt="", w=1200, cls="", loading="lazy", sizes="100vw", priority=False):
    """Responsive Sanity image with a small srcset. priority marks the page's main image (see img())."""
    if ref.startswith("http"):
        return img(ref, alt, cls, loading, sizes=sizes, priority=priority)
    if ref.startswith("/"):
        return img(S(ref, w), alt, cls, loading, sizes=sizes, priority=priority)
    _, ow, oh = sanity_id(ref)
    widths = sorted(set(x for x in (w // 2, w, w * 2) if not ow or x <= ow) or {ow})
    srcset = ", ".join("%s %dw" % (S(ref, x), x) for x in widths)
    dims = ' width="%d" height="%d"' % (ow, oh) if ow and oh else ""
    return img(S(ref, w), alt, cls, loading, 'srcset="%s" sizes="%s"%s' % (srcset, sizes, dims), priority=priority)


def photo(src, alt="", ratio="ratio-43", extra="", sizes="100vw"):
    return '<div class="photo %s %s">%s</div>' % (ratio, extra, img(src, alt, sizes=sizes))


def btn(label, href, kind=""):
    return '<a class="btn %s" href="%s">%s</a>' % (kind, href, label)


def money(v):
    if v is None:
        return ""
    return "${:,.0f}".format(round(float(v)))


def nice_date(iso):
    if not iso:
        return ""
    d = datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S") if "T" in iso else datetime.strptime(iso[:10], "%Y-%m-%d")
    if "T" in iso:
        d = d - timedelta(hours=6)   # Mountain time
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower().replace("&", "")).strip("-")


# ------------------------------------------------------------------ chrome
LOGO = VP("/images/sr-communities-logo.svg")
# Header logo, inline so its colors can adapt to whatever it sits on (see site.js)
LOGO_SVG = '<svg class="logo-svg" viewBox="0 0 337.36 125.66" aria-hidden="true" focusable="false"><g><g><path class="lg-word" d="M37.62,78.51v-13.13c4.45,3.11,10.94,5.44,16.66,5.44,3.95,0,5.65-1.27,5.65-3.74,0-1.55-.78-2.68-3.25-3.6l-6.42-1.91c-9.11-2.75-12.85-7.27-12.85-14.61,0-10.02,7.27-16.02,19.62-16.02,6.07,0,11.65,1.55,16.8,4.09v12.85c-4.73-2.82-10.02-4.45-14.89-4.45-4.09,0-5.86,1.06-5.86,3.11,0,1.62,1.27,2.61,3.81,3.39l5.22,1.41c9.88,2.61,14.33,7.41,14.33,15.39,0,10.38-7.48,16.66-20.33,16.66-6.28,0-12.56-1.55-18.49-4.87"/><path class="lg-word" d="M116.95,45.97v35.93h-13.83v-5.36c-1.84,3.53-5.79,6.42-10.87,6.42-8.89,0-12.85-6-12.85-14.82v-22.16h14.19v19.27c0,3.81,1.2,6.14,4.45,6.14s4.73-2.47,4.73-6.56v-18.85h14.19Z"/><path class="lg-word" d="M159.02,59.31v22.59h-14.19v-19.34c0-3.6-1.2-5.93-4.45-5.93s-4.8,2.54-4.8,6.14v19.13h-14.19v-35.93h13.9v5.08c1.77-3.39,5.44-6.14,11.08-6.14,7.91,0,12.63,5.36,12.63,14.4"/><path class="lg-word" d="M184,55.78c4.52,0,6.78-2.19,6.78-5.86s-2.12-5.44-6.07-5.44h-5.93v11.29h5.22ZM190.84,81.9l-12.07-19.06v19.06h-14.54v-49.41h23.15c11.58,0,19.06,5.72,19.06,15.88,0,7.06-3.67,12.49-11.51,14.12l12.92,19.41h-17.01Z"/><path class="lg-word" d="M211.1,45.97h14.19v35.93h-14.19v-35.93ZM210.67,36.3c0-4.02,2.96-6.78,7.48-6.78s7.41,2.75,7.41,6.78c0,4.24-3.11,6.92-7.41,6.92s-7.48-2.68-7.48-6.92"/><path class="lg-word" d="M282.94,60.44h11.79c-.21-3.53-2.26-5.36-5.72-5.36s-5.72,1.98-6.07,5.36M306.45,67.64h-23.29c1.48,2.89,5.08,4.8,11.15,4.8,3.95,0,7.55-.99,10.52-2.75v9.39c-2.75,2.05-7.62,3.88-14.4,3.88-13.48,0-21.81-7.41-21.81-19.2s7.84-18.85,19.83-18.85,18,6.35,18,18.14v4.59Z"/><path class="lg-word" d="M337.36,46.61v12.92c-1.2-.71-3.11-1.34-5.72-1.34-5.22,0-7.98,3.11-7.98,9.18v14.54h-14.19v-35.93h14.19v7.62c1.62-6.21,4.94-8.26,9.17-8.26,2.05,0,3.53.64,4.52,1.27"/><path class="lg-accent" d="M10.33,88.8l-1.32-.32.81,1.09s3.76,4.94,9.66,1.08c1.52-.99,2.62-2.6,3.68-4.15,1.04-1.52,2.03-2.96,3.35-3.83,1.81-1.18,3.46-.81,3.53-.79l1.32.32-.81-1.09s-.55-.72-1.53-1.39c-1.62-1.1-4.46-2.1-8.14.31-1.51.99-2.61,2.59-3.68,4.14-1.05,1.52-2.03,2.96-3.36,3.83-1.81,1.19-3.46.81-3.53.79M2.32,70.96l-1.14-.75.39,1.3c.02.06,1.85,5.94,8.71,4.32,1.77-.41,3.35-1.54,4.88-2.64,1.5-1.07,2.92-2.08,4.46-2.45,2.1-.5,3.53.43,3.59.47l1.13.75-.39-1.3s-.27-.87-.96-1.82c-1.14-1.59-3.47-3.5-7.75-2.49-1.76.41-3.35,1.54-4.87,2.64-1.5,1.07-2.92,2.09-4.46,2.45-2.1.49-3.53-.43-3.59-.47M4.11,53.12c-2.15-.25-3.17-1.61-3.21-1.67l-.81-1.09-.08,1.36c0,.06-.29,6.21,6.71,7.04,1.8.21,3.67-.31,5.49-.81,1.78-.49,3.46-.96,5.03-.77,2.15.26,3.17,1.61,3.21,1.67l.81,1.09.08-1.35s.04-.9-.28-2.04c-.53-1.89-2.06-4.47-6.43-4.99-1.8-.21-3.67.31-5.48.81-1.78.49-3.46.96-5.03.77M19.1,37.4c-1.62-.81-3.55-.97-5.43-1.11-1.84-.14-3.58-.28-4.99-.99-1.93-.97-2.43-2.6-2.45-2.66l-.39-1.31-.54,1.25c-.02.06-2.4,5.73,3.9,8.91,1.62.82,3.56.97,5.43,1.12,1.84.14,3.58.28,4.99.99,1.93.97,2.43,2.6,2.45,2.66l.39,1.3.54-1.25s.35-.84.44-2.02c.14-1.96-.41-4.91-4.34-6.89M28.14,25.65c-1.24-1.32-3.01-2.12-4.72-2.9-1.68-.77-3.27-1.49-4.35-2.64-1.48-1.57-1.39-3.27-1.39-3.34l.08-1.36-.94.99s-4.22,4.57.62,9.7c1.24,1.32,3.01,2.13,4.72,2.9,1.68.77,3.27,1.49,4.35,2.64,1.48,1.58,1.39,3.27,1.39,3.34l-.08,1.36.94-.99s.61-.66,1.1-1.74c.81-1.79,1.3-4.75-1.72-7.96M39.54,25.78c1.37-1.4,2.85-4.03,1.11-8.07-.72-1.66-2.1-3.03-3.44-4.34-1.32-1.29-2.56-2.52-3.19-3.97-.85-1.99-.19-3.55-.16-3.61l.54-1.25-1.22.61c-.06.03-5.52,2.85-2.74,9.33.72,1.67,2.1,3.03,3.44,4.34,1.32,1.29,2.56,2.52,3.18,3.97.85,1.99.19,3.55.16,3.62l-.54,1.25,1.21-.61s.81-.42,1.63-1.26M53.37,9.26c-.8-1.67-1.55-3.24-1.64-4.82-.12-2.16,1.03-3.4,1.08-3.45l.94-.99-1.35.15c-.06,0-6.17.79-5.76,7.83.1,1.81.94,3.56,1.75,5.26.8,1.67,1.55,3.24,1.64,4.82.12,2.16-1.03,3.4-1.08,3.45l-.94.99,1.35-.15s.9-.12,1.96-.63c1.77-.85,4.05-2.81,3.8-7.2-.1-1.81-.94-3.56-1.75-5.26M72.28,2.97l1.22-.61-1.32-.32c-.06-.01-6.06-1.37-8.09,5.39-.52,1.74-.34,3.67-.16,5.54.18,1.84.35,3.57-.11,5.09-.62,2.07-2.13,2.85-2.2,2.88l-1.22.61,1.32.32s.88.2,2.06.08c1.95-.2,4.77-1.25,6.03-5.47.52-1.73.34-3.67.15-5.54-.18-1.84-.34-3.57.11-5.09.62-2.07,2.13-2.84,2.2-2.87M89.89,11.49l1.35-.15-1.14-.75s-5.23-3.36-9.45,2.29c-1.08,1.45-1.57,3.34-2.04,5.16-.46,1.79-.9,3.48-1.84,4.74-1.29,1.73-2.98,1.94-3.05,1.95l-1.35.15,1.13.75s.76.49,1.91.78c1.9.48,4.91.45,7.54-3.08,1.08-1.45,1.57-3.33,2.04-5.15.46-1.79.9-3.48,1.85-4.75,1.29-1.73,2.98-1.94,3.05-1.95M104.84,25.83l-.81-1.09c-.03-.05-3.76-4.94-9.66-1.08-1.52.99-2.62,2.6-3.68,4.15-1.04,1.52-2.03,2.96-3.35,3.83-1.81,1.18-3.46.8-3.53.79l-1.32-.32.81,1.09s.55.72,1.53,1.39c1.62,1.1,4.46,2.1,8.14-.31,1.52-.99,2.61-2.59,3.68-4.14,1.05-1.52,2.03-2.96,3.36-3.83,1.81-1.19,3.46-.81,3.53-.79l1.32.32Z"/><polygon class="lg-word" points="270.03 45.99 255.77 81.92 241.37 81.92 227.19 45.99 242.29 45.99 248.5 65.12 254.93 45.99 270.03 45.99"/><g><path class="lg-accent" d="M98.71,116.43h2.16l-.83,6.95c-2.47,1.38-5.22,2.28-9.35,2.28-8.21,0-13.39-5.7-13.39-13.59,0-9.15,6.13-14.77,13.86-14.77,4.01,0,6.87,1.06,8.76,2.59v6.13h-2.12c-1.06-4.36-3.3-6.44-6.83-6.44-5.81,0-8.21,5.26-8.21,11.35,0,7.11,2.95,12.41,8.72,12.41,3.73,0,5.73-2.32,7.23-6.91Z"/><path class="lg-accent" d="M103.66,115.13c0-6.87,4.56-11.31,10.29-11.31,6.05,0,9.98,4.48,9.98,10.53,0,6.87-4.59,11.31-10.33,11.31-6.05,0-9.94-4.48-9.94-10.53ZM118.98,115.33c0-5.11-2-9.27-5.54-9.27-3.26,0-4.87,3.3-4.87,8.09,0,5.11,2,9.23,5.58,9.23,3.22,0,4.83-3.26,4.83-8.05Z"/><path class="lg-accent" d="M152.04,125.27v-1.77c1.77-.24,2.75-.43,2.75-2.24v-10.6c0-2.51-.86-3.38-3.14-3.38-1.81,0-3.46.71-4.83,1.65v12.33c0,1.81,1.02,2,2.75,2.24v1.77h-10.25v-1.77c1.77-.24,2.75-.43,2.75-2.24v-10.6c0-2.51-.86-3.38-3.1-3.38-1.85,0-3.5.71-4.87,1.65v12.33c0,1.81.94,2,2.71,2.24v1.77h-10.29v-1.77c1.73-.24,2.83-.43,2.83-2.24v-12.8l-2.63-1.69v-.98l6.28-2.04h1.1v4.01c1.81-1.88,4.01-3.93,7.27-3.93,2.67,0,4.56,1.26,5.22,4.08,1.85-1.88,4.28-4.08,7.58-4.08s5.38,1.92,5.38,6.4v11.04c0,1.81,1.06,2,2.83,2.24v1.77h-10.33Z"/><path class="lg-accent" d="M189.9,125.27v-1.77c1.77-.24,2.75-.43,2.75-2.24v-10.6c0-2.51-.86-3.38-3.14-3.38-1.81,0-3.46.71-4.83,1.65v12.33c0,1.81,1.02,2,2.75,2.24v1.77h-10.25v-1.77c1.77-.24,2.75-.43,2.75-2.24v-10.6c0-2.51-.86-3.38-3.1-3.38-1.85,0-3.5.71-4.87,1.65v12.33c0,1.81.94,2,2.71,2.24v1.77h-10.29v-1.77c1.73-.24,2.83-.43,2.83-2.24v-12.8l-2.63-1.69v-.98l6.28-2.04h1.1v4.01c1.81-1.88,4.01-3.93,7.27-3.93,2.67,0,4.56,1.26,5.22,4.08,1.85-1.88,4.28-4.08,7.58-4.08s5.38,1.92,5.38,6.4v11.04c0,1.81,1.06,2,2.83,2.24v1.77h-10.33Z"/><path class="lg-accent" d="M217.27,121.81c-1.77,1.85-4.01,3.85-7.31,3.85s-5.66-1.92-5.66-6.52v-10.29c0-1.3-.39-1.85-2.08-2.12l-.63-.12v-1.57l6.68-1.22h.83v14.73c0,2.59,1.02,3.77,3.26,3.77,1.88,0,3.53-.75,4.91-1.65v-11.82c0-1.3-.39-1.85-2.08-2.12l-.59-.12v-1.57l6.6-1.22h.86v16.77c0,1.33.35,1.73,1.96,1.88l.98.08v1.77l-6.87,1.34h-.86v-3.85Z"/><path class="lg-accent" d="M243.22,110.66c0-2.43-.98-3.38-3.3-3.38-1.85,0-3.81.71-5.14,1.65v12.33c0,1.81.98,2,2.75,2.24v1.77h-10.33v-1.77c1.73-.24,2.83-.43,2.83-2.24v-12.8l-2.63-1.69v-.98l6.28-2.04h1.1v4.01c1.81-1.88,4.24-3.93,7.54-3.93,3.53,0,5.66,1.92,5.66,6.44v11c0,1.81,1.06,2,2.83,2.24v1.77h-10.37v-1.77c1.77-.24,2.79-.43,2.79-2.24v-10.6Z"/><path class="lg-accent" d="M260.42,121.26c0,1.81,1.06,2,2.83,2.24v1.77h-10.41v-1.77c1.73-.24,2.83-.43,2.83-2.24v-12.84l-2.63-1.69v-.94l6.28-1.96h1.1v17.44ZM254.88,98.52c0-1.61,1.26-2.95,3.02-2.95s2.98,1.34,2.98,2.95-1.26,2.95-2.98,2.95-3.02-1.33-3.02-2.95Z"/><path class="lg-accent" d="M272.16,104.21h5.77v2.36h-5.77v13.24c0,2.08.9,2.83,2.91,2.83,1.1,0,2.4-.31,3.38-.83l.51,1.22c-1.49,1.61-3.65,2.63-6.36,2.63-3.14,0-5.18-1.49-5.18-5.11v-13.98h-2.79v-1.49c2.2-1.14,4.32-2.98,6.13-5.5h1.41v4.63Z"/><path class="lg-accent" d="M287.95,121.26c0,1.81,1.06,2,2.83,2.24v1.77h-10.41v-1.77c1.73-.24,2.83-.43,2.83-2.24v-12.84l-2.63-1.69v-.94l6.28-1.96h1.1v17.44ZM282.41,98.52c0-1.61,1.26-2.95,3.02-2.95s2.98,1.34,2.98,2.95-1.26,2.95-2.98,2.95-3.02-1.33-3.02-2.95Z"/><path class="lg-accent" d="M311.08,112.66v1.3h-13.71c0,4.75,2.67,7.93,6.83,7.93,2.79,0,4.63-1.3,6.05-3.18l.86.51c-.98,3.81-3.97,6.44-8.56,6.44-5.77,0-9.43-4.36-9.43-10.25,0-6.95,4.24-11.59,9.82-11.59s8.13,3.77,8.13,8.84ZM297.49,111.95h9.15c-.04-3.61-1.45-5.97-4.32-5.97s-4.52,2.79-4.83,5.97Z"/><path class="lg-accent" d="M314.02,123.62l-.24-5.07h2.04c.75,3.22,2.59,5.11,5.73,5.11,2.32,0,3.81-1.06,3.81-2.95,0-2.24-1.57-3.02-5.11-4.01-3.97-1.1-6.32-2.79-6.32-6.52s2.87-6.36,7.3-6.36c2.71,0,4.95.67,6.68,1.69v4.71h-2c-.59-2.87-2.16-4.36-4.83-4.36-2.04,0-3.22,1.22-3.22,2.83,0,1.92,1.3,2.95,4.52,3.81,4.04,1.1,6.83,2.47,6.83,6.6,0,3.89-2.91,6.56-7.78,6.56-2.83,0-5.5-.63-7.42-2.04Z"/></g></g></g></svg>'
FOOTER_BG = V("footer-rocks.16z_pgs-5dzer.jpg")

LIFE = [
    ("Live In", "/live-in", "Floor Plans. The Design Center. How We Build.", V("live-in.0-iialxva3p9u.jpg"), "Couple relaxing in a SunRiver Firelight home"),
    ("Live Out", "/live-out", "Southern Utah. Trails and Nearby Adventure.", V("hike.07ka4q1elcjrm.jpg"), "SunRiver members hiking in red rock country"),
    ("Live On", "/live-on", "Clubs and Activities. Events Calendar. Bucketlist.", V("live-on.2kwzvtocledst.jpg"), "SunRiver members enjoying a club activity"),
]
# Clark, Nov 2026: the phone menu uses these shorter lines under Live In, Live Out and Live On (the desktop dropdown keeps LIFE's)
LIFE_PHONE = {"Live In": "The home itself", "Live Out": "Everything past the front door", "Live On": "Everyone you have not met yet"}
NAV = [("homes", "Homes", "/homes-for-sale"), ("about", "About", "/about"), ("visit", "Visit", "/contact-us")]


def pill_header(active, variant="bar"):
    """Site header from the OFFICIAL SunRiver Website Figma file: logo plus the pill nav with the
    Life at SunRiver dropdown ("Home Clark Life NAV 6").
      variant "home"    : over the homepage hero, no tab ("Home Clark Life NAV 6")
      variant "overlay" : over a photo hero with the yellow Founders Club tab ("Homes for Sale / Model Homes")
      variant "bar"     : white 168px bar with shadow ("Homes for Sale Filter Simple", "Home Detail")"""
    from .figma_assets import FG
    items = "".join('<li><a href="%s" data-i="%d"><strong>%s</strong></a></li>' % (h, k, t) for k, (t, h, sub, _, _) in enumerate(LIFE))
    # Dropdown photo per item, Figma "Home NAV Live In 3": each photo carries a serif title, and it swaps as you hover.
    # The photos are 800 px copies made for this slot (389 px wide), and they carry data-src instead of src:
    # nothing downloads until a visitor goes to open the menu (see "menu photos" in site.js).
    shots = [("/media/fg/nav-menu-home.webp", "A couple cooking together in a SunRiver Firelight kitchen", "Your Home"),
             ("/media/fg/nav-menu-hike.webp", LIFE[1][4], "Southern Utah"),
             ("/media/fg/nav-menu-clubs.webp", "SunRiver members playing pickleball", "Clubs &amp; Groups")]
    photos = "".join('<span class="pd-shot%s" data-i="%d">%s<span class="pd-shot-title">%s</span></span>' % (" is-on" if k == 0 else "", k, deferred_img(src, alt), title)
                     for k, (src, alt, title) in enumerate(shots))
    cur = lambda k: ' aria-current="page"' if k == active else ""
    m_life = "\n".join('        <li><a class="m-nav-row m-nav-rich" href="%s"><span class="m-nav-title">%s<svg class="m-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg></span><span class="m-nav-desc">%s</span></a></li>'
                       % (href, name, LIFE_PHONE.get(name, desc)) for name, href, desc, _, _ in LIFE)
    tab = ""  # the Founders Club tab is retired
    # One header everywhere: logo plus the floating pill, no white bar behind it.
    cls = {"home": "site-header overlay is-home", "overlay": "site-header overlay", "bar": "site-header overlay on-light"}[variant]
    return '''<a class="skip" href="#main">Skip to content</a>
<header class="%s" data-menu="closed">
  %s
  <div class="wrap header-inner">
    <a class="logo" href="/" aria-label="SunRiver Communities home">%s</a>
    <a class="m-visit" href="/contact-us">Visit</a>
    <button class="menu-toggle" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="main-nav pill-nav" aria-label="Main">
      <span class="pill-morph" aria-hidden="true"></span>
      <div class="nav-item" data-open="false"><button class="nav-link" type="button" aria-expanded="false" aria-controls="life-menu"%s>Life at SunRiver<span class="chev" aria-hidden="true"></span></button>
        <div class="pill-drop" id="life-menu" data-active="0"><ul>%s</ul><div class="pill-drop-photo" aria-hidden="true">%s</div></div></div>
      <div class="nav-item has-sm" data-open="false"><button class="nav-link" type="button" aria-expanded="false" aria-controls="homes-menu"%s>Homes<span class="chev" aria-hidden="true"></span></button>
        <div class="pill-drop pill-drop-sm" id="homes-menu"><ul><li><a href="/floor-plans"><strong>Floor Plans</strong></a></li><li><a href="/homes-for-sale"><strong>Homes for Sale</strong></a></li></ul></div></div>
      <div class="nav-item"><a class="nav-link" href="/discovery-villas"%s>Discovery Villas</a></div>
      <a class="pill-cta" href="/contact-us"%s>Visit</a>
    </nav>
  </div>
</header>
<div class="m-nav" id="m-nav" role="dialog" aria-modal="true" aria-label="Menu" hidden>
  <div class="m-nav-bar">
    <a class="m-nav-logo" href="/" aria-label="SunRiver Communities home">%s</a>
    <a class="m-visit" href="/contact-us">Visit</a>
    <button class="m-nav-close" type="button" aria-label="Close menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  </div>
  <nav class="m-nav-body" aria-label="Mobile">
    <div class="m-nav-panels">
    <div class="m-nav-panel" data-panel="main">
      <ul class="m-nav-list">
        <li><button type="button" class="m-nav-row" data-go="life" aria-expanded="false">Life at SunRiver<svg class="m-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg></button></li>
        <li><button type="button" class="m-nav-row" data-go="homes" aria-expanded="false">Homes<svg class="m-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg></button></li>
        <li><a class="m-nav-row" href="/discovery-villas">Discovery Villas</a></li>
        <li><a class="m-nav-row" href="/contact-us">Visit</a></li>
      </ul>
      <div class="m-nav-more">
        <p class="m-nav-label">More</p>
        <ul class="m-nav-small"><li><a href="/about">About</a></li><li><a href="/contact-us">Contact Us</a></li><li><a href="/bucketlistliving">Bucketlist Living</a></li></ul>
      </div>
    </div>
    <div class="m-nav-panel" data-panel="life" aria-hidden="true" inert>
      <button type="button" class="m-nav-back" data-go="main"><svg class="m-back-chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>Back</button>
      <p class="m-nav-label">Life at SunRiver</p>
      <ul class="m-nav-list">
%s
      </ul>
    </div>
    <div class="m-nav-panel" data-panel="homes" aria-hidden="true" inert>
      <button type="button" class="m-nav-back" data-go="main"><svg class="m-back-chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>Back</button>
      <p class="m-nav-label">Homes</p>
      <ul class="m-nav-list">
        <li><a class="m-nav-row" href="/floor-plans">Floor Plans<svg class="m-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg></a></li>
        <li><a class="m-nav-row" href="/homes-for-sale">Homes for Sale<svg class="m-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg></a></li>
      </ul>
    </div>
    </div>
  </nav>
</div>
''' % (cls, tab, LOGO_SVG, cur("life"), items, photos,
       cur("homes"), cur("villas"), cur("visit"), LOGO_SVG, m_life)


def header(active):
    """Every page uses the pill nav. "home-overlay" is the homepage; an active key ending in "-overlay"
    puts the header over that page's photo hero with the Founders tab; everything else gets the white bar."""
    if active == "home-overlay":
        return pill_header("", "home")
    if active.endswith("-overlay"):
        return pill_header(active[:-8], "overlay")
    return pill_header(active, "bar")


SOCIAL = '''<div class="social">
  <a href="https://facebook.com/sunriver" aria-label="SunRiver on Facebook"><svg viewBox="0 0 24 24"><path d="M14 8h3V4h-3c-2.8 0-4 1.7-4 4.3V10H7v4h3v8h4v-8h3l1-4h-4V8.6c0-.4.3-.6.6-.6H14z"/></svg></a>
  <a href="https://instagram.com/sunriver_communities/" aria-label="SunRiver on Instagram"><svg viewBox="0 0 24 24"><path d="M12 7.3A4.7 4.7 0 1 0 12 16.7 4.7 4.7 0 0 0 12 7.3zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm6-7.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0zM12 2.5c-2.6 0-2.9 0-3.9.1C4.6 2.7 2.7 4.6 2.6 8.1 2.5 9.1 2.5 9.4 2.5 12s0 2.9.1 3.9c.1 3.5 2 5.4 5.5 5.5 1 .1 1.3.1 3.9.1s2.9 0 3.9-.1c3.5-.1 5.4-2 5.5-5.5.1-1 .1-1.3.1-3.9s0-2.9-.1-3.9c-.1-3.5-2-5.4-5.5-5.5-1-.1-1.3-.1-3.9-.1zm0 1.7c2.5 0 2.8 0 3.8.1 2.6.1 3.8 1.3 3.9 3.9.1 1 .1 1.3.1 3.8s0 2.8-.1 3.8c-.1 2.6-1.3 3.8-3.9 3.9-1 .1-1.3.1-3.8.1s-2.8 0-3.8-.1c-2.6-.1-3.8-1.3-3.9-3.9-.1-1-.1-1.3-.1-3.8s0-2.8.1-3.8C4.3 5.5 5.5 4.3 8.2 4.3c1-.1 1.3-.1 3.8-.1z"/></svg></a>
  <a href="https://www.youtube.com/@sunriver_communities" aria-label="SunRiver on YouTube"><svg viewBox="0 0 24 24"><path d="M23 7.2s-.2-1.6-.9-2.3c-.9-.9-1.9-.9-2.3-1C16.6 3.6 12 3.6 12 3.6s-4.6 0-7.8.3c-.4.1-1.4.1-2.3 1C1.2 5.6 1 7.2 1 7.2S.8 9.1.8 11v1.8c0 1.9.2 3.8.2 3.8s.2 1.6.9 2.3c.9.9 2 .9 2.6 1 1.8.2 7.5.2 7.5.2s4.6 0 7.8-.3c.4-.1 1.4-.1 2.3-1 .7-.7.9-2.3.9-2.3s.2-1.9.2-3.8V11c0-1.9-.2-3.8-.2-3.8zM9.7 15.1V8.5l6 3.3-6 3.3z"/></svg></a>
</div>'''

FOOTER_COLS = [
    ("Company", [("Why SunRiver?", "/why-sunriver"), ("About", "/about"), ("Southern Utah", "/southern-utah"), ("FAQ", "/faq"), ("History", "/history")]),
    ("Find a Home", [("Homes for Sale", "/homes-for-sale"), ("Mortgage Options", "/no-mortgage-payments-for-life"), ("Energy Efficient Homes", "/energy"), ("Design Center", "/design")]),
    # Clark, Nov 2026: St. George and Villas are shown by name only (no link, no page); SunRiver Firelight is the one to explore
    ("Communities", [("SunRiver St. George", None), ("SunRiver Firelight", "/sunriver-firelight"), ("SunRiver Villas", None)]),
    # Clark, Nov 2026: the SunRiverToday.com and SRvillasToday.com links are gone; the St. George and Villas contacts are on their own page
    ("Get in Touch", [("Contact Us", "/contact-us"), ("Bucketlistliving Blog", "/bucketlistliving"),
                      ("Previous Community Information", "/previous-communities"), ("Privacy Policy", "/privacy-policy")]),
]


def footer():
    """Footer matching the live sunriver.com footer: the couple-on-red-rock photo behind everything, social icons
    centered, the logo with address and phone on the left, four link columns."""
    from .figma_assets import FG
    cols = "".join('<div class="footer-col"><h2>%s</h2><ul>%s</ul></div>' % (
        t, "".join(('<li><a href="%s"%s>%s</a></li>' % (h, ' class="italic"' if l == "Privacy Policy" else "", l)) if h else '<li><span class="footer-name">%s</span></li>' % l for l, h in links))
        for t, links in FOOTER_COLS)
    return '''<footer class="site-footer">
  %s
  <div class="wrap">
    %s
    <div class="footer-grid">
      <div class="footer-brand">%s<p>182 Cottonwood Dr<br>Toquerville, UT 84774</p><p><a href="%s">Sales Office: %s</a></p></div>
      %s
    </div>
  </div>
</footer>''' % (img(FG("footer-photo"), "", "footer-bg"), SOCIAL, '<a class="footer-logo" href="/" aria-label="SunRiver Communities home">%s</a>' % LOGO_SVG, PHONE_TEL, PHONE, cols)


FONTS = '''<style>
@font-face{font-family:"ABC Ginto";src:url("%s") format("opentype");font-weight:500;font-style:normal;font-display:swap}
@font-face{font-family:"ABC Ginto";src:url("%s") format("opentype");font-weight:900;font-style:normal;font-display:swap}
@font-face{font-family:"Tiempos Text";src:url("%s") format("opentype");font-weight:500;font-style:normal;font-display:swap}
</style>''' % (V("ABCGintoMedium-s.p.1gnfcs1mxia21.otf"), V("ABCGintoBlack-s.p.06eqbvszkm88h.otf"), V("TiemposTextMedium-s.p.1nnfz5h4rihgs.otf"))


def add(path, title, description, active, body, body_class=""):
    full_title = title if SITE_NAME in title else "%s | %s" % (title, SITE_NAME)
    if body.lstrip().startswith('<section class="fah-hero') and not active.endswith("-overlay"):
        active = (active or "page") + "-overlay"  # full photo hero: the header and nav sit on the photo
    if active.endswith("-overlay") and active != "home-overlay":
        body_class = (body_class + " overlay-page").strip()
    body = place_sizes(body)
    doc = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta name="theme-color" content="#325A96" media="(width: 382px), (width: 594px) and (max-height: 420px)">
<link rel="icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.sanity.io">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@500;700;900&family=Source+Serif+4:opsz,wght@8..60,500&display=swap">
%s
%s
<link rel="stylesheet" href="/assets/styles.css?v=%s">
%s
</head>
<body%s>
%s
<main id="main">
%s
</main>
%s
<script src="/assets/site.js?v=%s" defer></script>
</body>
</html>
''' % (esc(full_title), esc(description), esc(full_title), esc(description), FONTS, preload_link(body), asset_v("styles.css"), TRACKING,
       ' class="%s"' % body_class if body_class else "", header(active), body, footer(), asset_v("site.js"))
    assert "—" not in doc, "em dash found on %s" % path
    PAGES[path] = doc


# ------------------------------------------------------------------ components
def chat_section(title="Ready to Chat?", intro="Ready to take the next step and speak with an agent about your next home? Fill out the form below and we'll reach out as soon as possible.", fid="chat", hs="general"):
    """The sitewide "Ready to Chat?" form. Fields match the HubSpot form it feeds (hs is a key of HS_FORMS):
    first name, last name, email and at least one interest. Phone is optional and saved to the contact as well."""
    checks = "\n".join('          <label><input type="checkbox" name="what_are_you_interested_in_" value="%s">%s</label>' % (esc(v), esc(l)) for l, v in HS_INTERESTS)
    return '''<section class="section yellow-bg chat" id="%(fid)s" aria-labelledby="%(fid)s-title">
  <div class="wrap">
    <h2 id="%(fid)s-title">%(title)s</h2>
    <hr class="rule">
    <p>%(intro)s</p>
    <form class="chat-form" %(hs)s novalidate>
      <div class="row">
        <div><label for="%(fid)s-first">First Name</label><input id="%(fid)s-first" name="firstname" type="text" autocomplete="given-name" required></div>
        <div><label for="%(fid)s-last">Last Name</label><input id="%(fid)s-last" name="lastname" type="text" autocomplete="family-name" required></div>
      </div>
      <div class="row">
        <div><label for="%(fid)s-email">Email Address</label><input id="%(fid)s-email" name="email" type="email" autocomplete="email" required></div>
        <div><label for="%(fid)s-phone">Phone</label><input id="%(fid)s-phone" name="phone" type="tel" autocomplete="tel"></div>
      </div>
      <fieldset data-required="Please choose at least one."><legend>What are you interested in?</legend>
        <div class="checks">
%(checks)s
        </div>
      </fieldset>
      %(hp)s
      <p class="consent">By clicking "Submit", I authorize SunRiver to contact me about this request via the contact information I provide. I understand calls or texts may use automated technology. I can opt out at any time on the SunRiver website or by unsubscribing. This consent is not required to complete my request.</p>
      <button class="btn sand-btn" type="submit">Submit</button>
      <p class="form-note" role="status" hidden></p>
    </form>
  </div>
</section>''' % dict(fid=fid, title=title, intro=intro, hs=hs_attrs(hs), checks=checks, hp=HONEYPOT)


def dv_book_form(key="villas"):
    """The Discovery Villas request-a-stay form, shared by /discovery-villas/book and the Meta ad landing page.
    `key` picks the HubSpot form it feeds (a key of HS_FORMS). HubSpot gets name, email, mobile phone and the arrival
    date; checkout, guests and notes ride along in the message. Checkout fills in from the arrival date (site.js)."""
    return '''<form class="chat-form light dvb-form" %s novalidate aria-label="Request a Discovery Villas stay">
      <div class="row">
        <div><label for="dv-first">First name</label><input id="dv-first" name="firstname" type="text" autocomplete="given-name" required></div>
        <div><label for="dv-last">Last name</label><input id="dv-last" name="lastname" type="text" autocomplete="family-name" required></div>
      </div>
      <div class="row">
        <div><label for="dv-email">Email</label><input id="dv-email" name="email" type="email" autocomplete="email" required></div>
        <div><label for="dv-phone">Mobile phone</label><input id="dv-phone" name="mobilephone" type="tel" autocomplete="tel" required></div>
      </div>
      <div class="row">
        <div><label for="dv-arrive">Arrival date</label><input id="dv-arrive" name="date_of_requested_stay" type="date" data-hs-date required></div>
        <div><label for="dv-depart">Checkout</label><input id="dv-depart" name="checkout" type="date" data-hs-note="Checkout" readonly tabindex="-1" aria-describedby="dv-depart-note"><span class="dvb-hint" id="dv-depart-note">Two nights after arrival</span></div>
      </div>
      <div class="row">
        <div><label for="dv-guests">Guests</label><select id="dv-guests" name="guests" data-hs-note="Guests"><option>1</option><option selected>2</option><option>3</option><option>4</option></select></div>
        <div><label for="dv-from">Traveling from</label><input id="dv-from" name="city" type="text" autocomplete="address-level2" placeholder="City, State"></div>
      </div>
      <div><label for="dv-msg">Questions or notes</label><textarea id="dv-msg" name="message" placeholder="Flexible dates, accessibility needs, anything we should know"></textarea></div>
      <p class="consent">By clicking "Request my stay", I authorize SunRiver to contact me about this request via the contact information I provide. I understand calls or texts may use automated technology. I can opt out at any time on the SunRiver website or by unsubscribing. This consent is not required to complete my request.</p>
      %s
      <button class="btn" type="submit">Request my stay</button>
      <p class="form-note" role="status" hidden style="color:var(--sunriver-blue)"></p>
    </form>''' % (hs_attrs(key), HONEYPOT)


def full_hero(title, sub="", eyebrow="", src=None, alt="", cta=None, pos="50% 40%", extra="", tag="h1", cls=""):
    """The sitewide page hero: a full-bleed photo that runs up under the floating header (like Homes for Sale),
    a white wash at the top for the logo and nav, a blue tint behind a white title with a yellow underline."""
    from .figma_assets import FG
    src = src or FG("hfs-hero")
    e = '<p class="fh-eyebrow">%s</p>' % eyebrow if eyebrow else ""
    sb = '<p class="fh-sub">%s</p>' % sub if sub else ""
    c = '<div class="fh-cta">%s</div>' % cta if cta else ""
    return ('<section class="fah-hero fh-hero%s">%s<div class="wrap fah-hero-inner">%s<%s>%s</%s>%s%s</div>%s</section>' % (
        " " + cls if cls else "", img(src, alt, "fah-hero-img", "eager", 'style="object-position:%s"' % pos), e, tag, title, tag, sb, c, extra))


def sand_hero(eyebrow, title, sub="", tag="h1", src=None, alt="", pos="50% 40%"):
    return full_hero(title, sub, eyebrow, src, alt, tag=tag, pos=pos)


ABOUT_TABS = [("About Us", "/about"), ("Southern Utah", "/southern-utah"), ("FAQ", "/faq"), ("History", "/history")]  # same order as the footer


def yellow_hero(title_html, current, src=None, alt="", pos="50% 40%"):
    tabs = "".join('<li><a href="%s"%s>%s</a></li>' % (h, ' aria-current="page"' if h == current else "", t) for t, h in ABOUT_TABS)
    return full_hero(title_html, src=src, alt=alt, pos=pos) + '<nav class="tabbar" aria-label="About SunRiver"><ul>%s</ul></nav>' % tabs


def photo_hero(eyebrow, title, sub, src, alt, cta=None, pos="50% 40%"):
    return full_hero(title, sub, eyebrow, src, alt, cta, pos)


def banner(text_html, src, cta=None, tall=False, tag="h2"):
    return '<section class="banner%s">%s<div class="wrap"><%s>%s</%s>%s</div></section>' % (
        " tall" if tall else "", img(src, ""), tag, text_html, tag, cta or "")


def band(src, alt="", height="clamp(220px, 32vw, 460px)"):
    return '<div class="band" style="height:%s">%s</div>' % (height, img(src, alt))


def ul(items):
    return "<ul>" + "".join("<li>%s</li>" % i for i in items) + "</ul>"


def star_list(items, cls=""):
    return '<ul class="star-list %s">%s</ul>' % (cls, "".join("<li>%s</li>" % i for i in items))


def faq(q, a):
    return '<details class="faq"><summary>%s</summary><div class="answer">%s</div></details>' % (q, a)


FOUNDERS_BADGE = V("founders-badge.164umvg6w-3uo.png")
