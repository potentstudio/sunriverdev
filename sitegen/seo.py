"""Search and sharing basics, added to every page after it is rendered (build.py calls apply() just before writing).

What each page gets in its <head>:
  - a canonical link and og:url on the launch domain (SITE_URL), so previews and old hosts never compete with it
  - og:type, og:site_name, og:image and a Twitter card, so a shared link shows a photo
  - schema markup (JSON-LD): the business on the homepage and contact page, breadcrumbs on inner pages,
    BlogPosting on Bucketlist Living posts and FAQPage on /faq
  - "noindex" on the pages in NOINDEX (drafts and ad landing pages), which are also left out of the sitemap

It also writes /sitemap.xml and /robots.txt. Every fact in the markup (name, address, phone, social links) is read
from what the site already shows; nothing here is invented, and anything unknown (hours, map coordinates) is left out.
"""
import json
import re
from html import unescape

from . import lib

SITE_URL = "https://www.sunriver.com"  # the launch domain; the current sunriver.com uses www as its canonical host
SHARE_IMAGE = "/assets/img/share.jpg"  # 1200x630, the homepage photo; used when a page has no photo of its own

# Kept out of Google and out of the sitemap: drafts awaiting approval, pages only ads link to, and the error page.
NOINDEX = {
    "/404",
    "/discovery-villas-v2",    # draft
    "/sunriver-firelight-v2",  # draft
    "/firelight-bing",         # Microsoft Ads landing page
    "/discovery-villas-meta",  # Meta ads landing page
}

ADDRESS = {"@type": "PostalAddress", "streetAddress": "182 Cottonwood Dr", "addressLocality": "Toquerville",
           "addressRegion": "UT", "postalCode": "84737", "addressCountry": "US"}  # the footer's sales office address
ORG_ID = SITE_URL + "/#organization"


def _abs(url):
    return url if url.startswith("http") else SITE_URL + url


def _title(doc):
    m = re.search(r"<title>(.*?)</title>", doc, re.S)
    return unescape(m.group(1)).split(" | ")[0].strip() if m else ""


def _description(doc):
    m = re.search(r'<meta name="description" content="(.*?)">', doc, re.S)
    return unescape(m.group(1)) if m else ""


def _text(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def _social():
    return re.findall(r'href="(https://[^"]+)"', lib.SOCIAL)


def _detail(path):
    """Pages about one thing with its own photo: a floor plan, a listing or a post."""
    return bool(re.match(r"^/(floor-plans|homes-for-sale|bucketlistliving)/(?!page/|category/)[^/]+$", path))


def _share_image(path, doc, dist):
    """The photo a shared link shows. Detail pages use their own first photo, cropped to 1200x630 as a JPG (Sanity does
    that on its CDN; a photo in the repo is converted here). Every other page uses the sitewide share image."""
    if _detail(path):
        main = doc.split("<main", 1)[-1]
        m = re.search(r'<img[^>]+src="([^"]+)"', main)
        src = unescape(m.group(1)) if m else ""
        if src.startswith("https://cdn.sanity.io/images/"):
            return src.split("?")[0] + "?w=1200&h=630&fit=crop&fm=jpg&q=80"
        local = src.split("?")[0]
        if local.startswith("/") and dist is not None and (dist / local.lstrip("/")).is_file():
            try:
                from PIL import Image, ImageOps
                out = dist / "assets" / "share" / (path.strip("/").replace("/", "-") + ".jpg")
                out.parent.mkdir(parents=True, exist_ok=True)
                ImageOps.fit(Image.open(dist / local.lstrip("/")).convert("RGB"), (1200, 630)).save(out, quality=82)
                return SITE_URL + "/assets/share/" + out.name
            except Exception:  # noqa: BLE001  no Pillow, or not an image: fall back to the sitewide photo
                pass
    return SITE_URL + SHARE_IMAGE


def _organization():
    return {"@type": "HomeAndConstructionBusiness", "@id": ORG_ID, "name": lib.SITE_NAME,
            "parentOrganization": {"@type": "Organization", "name": "SunRiver Communities"},
            "url": SITE_URL + "/", "image": SITE_URL + SHARE_IMAGE,
            "telephone": lib.PHONE_TEL.replace("tel:", ""), "address": ADDRESS, "sameAs": _social()}


def _breadcrumbs(path, pages):
    parts = path.strip("/").split("/")
    items = [("Home", SITE_URL + "/")]
    for i in range(1, len(parts) + 1):
        p = "/" + "/".join(parts[:i])
        if p in pages:  # skip levels that are not pages themselves, like /bucketlistliving/category
            items.append((_title(pages[p]), SITE_URL + p))
    if len(items) < 2:
        return None
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": n, "name": name, "item": url} for n, (name, url) in enumerate(items, 1)]}


def _faq(doc):
    qa = re.findall(r'<details class="faq"><summary>(.*?)</summary><div class="answer">(.*?)</div></details>', doc, re.S)
    if not qa:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": _text(q), "acceptedAnswer": {"@type": "Answer", "text": _text(a)}} for q, a in qa]}


def _schema(path, doc, pages, posts, image):
    graph = []
    if path == "/":
        graph.append({"@type": "WebSite", "@id": SITE_URL + "/#website", "url": SITE_URL + "/", "name": lib.SITE_NAME,
                      "publisher": {"@id": ORG_ID}})
    if path in ("/", "/contact-us", "/about"):
        graph.append(_organization())
    if path != "/":
        crumbs = _breadcrumbs(path, pages)
        if crumbs:
            graph.append(crumbs)
    if path == "/faq":
        faq = _faq(doc)
        if faq:
            graph.append(faq)
    post = posts.get(path)
    if post:
        item = {"@type": "BlogPosting", "headline": _title(doc), "description": _description(doc), "image": image,
                "mainEntityOfPage": SITE_URL + path, "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}}
        if post.get("publishDate"):
            item["datePublished"] = post["publishDate"]
        if not any(g.get("@id") == ORG_ID for g in graph):
            graph.append(_organization())
        graph.append(item)
    if not graph:
        return ""
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">%s</script>' % data.replace("</", "<\\/")


def apply(pages, posts=(), dist=None):
    """Add the head tags to every page in `pages` (path -> html) in place, and return the sitemap and robots text."""
    by_path = {"/bucketlistliving/%s" % p["slug"]: p for p in posts if p.get("slug")}
    originals = dict(pages)
    for path, doc in originals.items():
        if path in NOINDEX:
            tags = ['<meta name="robots" content="noindex, follow">']
        else:
            url = SITE_URL + ("/" if path == "/" else path)
            image = _share_image(path, doc, dist)
            tags = ['<link rel="canonical" href="%s">' % url,
                    '<meta property="og:url" content="%s">' % url,
                    '<meta property="og:type" content="%s">' % ("article" if path in by_path else "website"),
                    '<meta property="og:site_name" content="%s">' % lib.esc(lib.SITE_NAME),
                    '<meta property="og:image" content="%s">' % lib.esc(image),
                    '<meta property="og:image:width" content="1200">',
                    '<meta property="og:image:height" content="630">',
                    '<meta name="twitter:card" content="summary_large_image">',
                    '<meta name="twitter:image" content="%s">' % lib.esc(image)]
            schema = _schema(path, doc, originals, by_path, image)
            if schema:
                tags.append(schema)
        marker = '<link rel="icon" href="/favicon.ico">'
        assert marker in doc, "no <head> marker on %s" % path
        pages[path] = doc.replace(marker, "\n".join(tags) + "\n" + marker, 1)

    listed = sorted(p for p in pages if p not in NOINDEX)
    rows = []
    for p in listed:
        post = by_path.get(p)
        lastmod = "<lastmod>%s</lastmod>" % post["publishDate"][:10] if post and post.get("publishDate") else ""
        rows.append("  <url><loc>%s%s</loc>%s</url>" % (SITE_URL, "/" if p == "/" else p, lastmod))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % "\n".join(rows)
    robots = "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL
    return sitemap, robots
