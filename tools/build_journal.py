#!/usr/bin/env python3
"""Rebuild the Journal listing and the RSS feed from tools/journal.json.

Usage, from the repository root:  python3 tools/build_journal.py

To add a piece: add an entry to tools/journal.json (any order; the newest
date leads), run this script, then commit journal.html, feed.xml and the
JSON together. It rewrites only the parts of journal.html between the
JOURNAL markers, and the whole of feed.xml.
"""
import html, json, os, re, sys
from datetime import datetime
from email.utils import format_datetime

SITE = "https://www.sircusmagazine.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRIES = os.path.join(ROOT, "tools", "journal.json")
PAGE = os.path.join(ROOT, "journal.html")
FEED = os.path.join(ROOT, "feed.xml")

e = lambda s: html.escape(s, quote=True)


def load():
    with open(ENTRIES, encoding="utf-8") as f:
        items = json.load(f)
    for it in items:
        it["dt"] = datetime.fromisoformat(it["published"])
    items.sort(key=lambda it: it["dt"], reverse=True)
    return items


def human(dt):
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def card(it, lead=False):
    src = it["card_large"] if lead else it["card"]
    loading = 'fetchpriority="high"' if lead else 'loading="lazy" decoding="async"'
    return (
        f'<a class="jr-card" href="{e(it["path"])}">\n'
        f'  <div class="jr-media"><img src="{e(src)}" alt="{e(it["alt"])}" {loading} style="object-position:{e(it["focus"])}"></div>\n'
        f'  <div class="jr-copy">\n'
        f'    <p class="jr-meta"><span class="jr-kind">{e(it["kind"])}</span><span class="jr-issue">{e(it["issue"])}</span></p>\n'
        f'    <h{2 if lead else 3} class="jr-name">{e(it["title"])}</h{2 if lead else 3}>\n'
        f'    <p class="jr-dek">{e(it["dek"])}</p>\n'
        f'    <p class="jr-by"><span>{e(it["credit"])}</span><time datetime="{it["dt"].date().isoformat()}">{human(it["dt"])}</time></p>\n'
        f'    <span class="jr-cta">{e(it["cta"])} &rarr;</span>\n'
        f'  </div>\n'
        f'</a>'
    )


def listing(items):
    lead, rest = items[0], items[1:]
    out = ['<section class="jr-lead jr-wrap" aria-label="Latest">', card(lead, True), '</section>']
    if rest:
        out += ['<section class="jr-grid jr-wrap" aria-label="Earlier">']
        out += [card(it) for it in rest]
        out += ['</section>']
    return "\n".join(out)


def jsonld(items):
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": SITE + "/journal",
        "url": SITE + "/journal",
        "name": "The Journal | SIRCUS Magazine",
        "description": "Editorials and cover stories from SIRCUS Magazine, newest first.",
        "isPartOf": {"@type": "WebSite", "name": "SIRCUS Magazine", "url": SITE + "/"},
        "mainEntity": {
            "@type": "ItemList",
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "numberOfItems": len(items),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": SITE + it["path"], "name": it["title"]}
                for i, it in enumerate(items)
            ],
        },
    }
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>"


def feed(items):
    def x(s):
        return html.escape(s, quote=False)

    newest = items[0]["dt"]
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/" xmlns:dc="http://purl.org/dc/elements/1.1/">',
        "<channel>",
        "<title>SIRCUS Magazine: The Journal</title>",
        f"<link>{SITE}/journal</link>",
        f'<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>',
        "<description>Editorials and cover stories from SIRCUS Magazine, newest first.</description>",
        "<language>en-us</language>",
        f"<copyright>{newest.year} SIRCUS Magazine</copyright>",
        f"<lastBuildDate>{format_datetime(newest)}</lastBuildDate>",
        "<image>",
        f"<url>{SITE}/favicon-96x96.png</url>",
        "<title>SIRCUS Magazine: The Journal</title>",
        f"<link>{SITE}/journal</link>",
        "<width>96</width><height>96</height>",
        "</image>",
    ]
    for it in items:
        url = SITE + it["path"]
        img = SITE + it["image"]
        size = os.path.getsize(os.path.join(ROOT, it["image"].lstrip("/")))
        body = (
            f'<p><a href="{url}"><img src="{img}" alt="{e(it["alt"])}" width="600" style="max-width:100%;height:auto"></a></p>'
            f'<p>{e(it["dek"])}</p><p>{e(it["credit"])}. {e(it["kind"])}, {e(it["issue"])}.</p>'
            f'<p><a href="{url}">{e(it["cta"])}</a></p>'
        )
        parts += [
            "<item>",
            f"<title>{x(it['title'])}</title>",
            f"<link>{url}</link>",
            f'<guid isPermaLink="true">{url}</guid>',
            f"<pubDate>{format_datetime(it['dt'])}</pubDate>",
            f"<category>{x(it['kind'])}</category>",
            f"<dc:creator>SIRCUS Magazine</dc:creator>",
            f"<description><![CDATA[{body}]]></description>",
            f'<enclosure url="{img}" length="{size}" type="image/jpeg"/>',
            f'<media:content url="{img}" medium="image" type="image/jpeg"><media:description>{x(it["alt"])}</media:description></media:content>',
            "</item>",
        ]
        if "]]>" in body:
            sys.exit(f"Entry {it['title']} contains ']]>', which would break the feed")
    parts += ["</channel>", "</rss>", ""]
    return "\n".join(parts)


def replace(text, name, body):
    pat = re.compile(rf"(<!-- JOURNAL:{name}:START -->).*?(<!-- JOURNAL:{name}:END -->)", re.S)
    if not pat.search(text):
        sys.exit(f"Marker JOURNAL:{name} not found in journal.html")
    return pat.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(2), text)


def main():
    items = load()
    for it in items:
        for key in ("card", "card_large", "image"):
            if not os.path.exists(os.path.join(ROOT, it[key].lstrip("/"))):
                sys.exit(f"Missing file for {it['title']}: {it[key]}")
    with open(PAGE, encoding="utf-8") as f:
        page = f.read()
    page = replace(page, "LIST", listing(items))
    page = replace(page, "LD", jsonld(items))
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(page)
    with open(FEED, "w", encoding="utf-8") as f:
        f.write(feed(items))
    print(f"Journal rebuilt: {len(items)} pieces, newest {items[0]['title']}.")


if __name__ == "__main__":
    main()
