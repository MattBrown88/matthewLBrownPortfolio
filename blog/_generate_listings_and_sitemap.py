#!/usr/bin/env python3
"""Regenerate the blog listings and sitemap from post frontmatter.

Called by blog/build.sh — not usually run directly.

Reads every Markdown file in blog/_posts/, parses its frontmatter
(title, date, tags, summary/description), and rewrites:

  - blog/index.html : all posts as cards + tag filter bar,
                      between the blog:cards / blog:filters markers
  - index.html      : the HOME_POST_COUNT most recent posts,
                      between the blog:latest markers
  - sitemap.xml     : home, blog index, and every published post

Posts without frontmatter are treated as drafts and skipped.
"""

import html
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "blog" / "_posts"
BASE_URL = "https://www.matthewlbrown.com"
HOME_POST_COUNT = 3

DATE_FORMATS = ("%B %d, %Y", "%b %d, %Y", "%B %Y", "%b %Y")


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    meta = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if key == "tags":
            value = [t.strip() for t in value.strip("[]").split(",") if t.strip()]
        else:
            value = value.strip("'\"")
        meta[key] = value
    return meta


def parse_date(raw):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def load_posts():
    posts, drafts = [], []
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta = parse_frontmatter(path.read_text())
        if meta is None or "title" not in meta:
            drafts.append(path.name)
            continue
        date = parse_date(meta.get("date", ""))
        if date is None:
            print(f"WARNING: unparseable date {meta.get('date')!r} in {path.name}")
            date = datetime.min
        posts.append({
            "slug": path.stem,
            "title": meta["title"],
            "date": date,
            "date_display": date.strftime("%b %Y") if date != datetime.min else "",
            "tags": meta.get("tags", []),
            "excerpt": meta.get("summary") or meta.get("description", ""),
        })
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts, drafts


def render_card(post):
    esc = html.escape
    tags = "".join(
        f'\n                <span class="blog-tag">{esc(t)}</span>'
        for t in post["tags"]
    )
    data_tags = esc("|".join(post["tags"]))
    return f'''        <div class="column is-one-third-desktop is-half-tablet blog-grid-item" data-tags="{data_tags}">
          <a class="blog-card" href="/blog/{post["slug"]}.html">
            <div class="blog-card-body">
              <span class="blog-card-date">{esc(post["date_display"])}</span>
              <h2 class="blog-card-title">{esc(post["title"])}</h2>
              <p class="blog-card-excerpt">{esc(post["excerpt"])}</p>
            </div>
            <div class="blog-card-band">
              <span class="blog-card-tags">{tags}
              </span>
              <span class="blog-card-more">Read More <i class="fa-solid fa-arrow-right"></i></span>
            </div>
          </a>
        </div>'''


def render_filters(posts):
    # Tags ordered by frequency so the most useful filters come first.
    counts = {}
    for post in posts:
        for tag in post["tags"]:
            counts[tag] = counts.get(tag, 0) + 1
    ordered = sorted(counts, key=lambda t: (-counts[t], t.lower()))
    pills = "".join(
        f'\n        <button class="blog-filter" type="button" data-filter="{html.escape(t)}">{html.escape(t)}</button>'
        for t in ordered
    )
    return (f'        <button class="blog-filter is-active" type="button" data-filter="">All</button>'
            f'{pills}')


def inject(path, marker, content):
    text = path.read_text()
    start, end = f"<!-- {marker}:start -->", f"<!-- {marker}:end -->"
    if start not in text or end not in text:
        sys.exit(f"ERROR: markers {start} / {end} not found in {path}")
    new = re.sub(
        re.escape(start) + r".*?" + re.escape(end),
        start + "\n" + content + "\n        " + end,
        text,
        flags=re.S,
    )
    path.write_text(new)


def write_sitemap(posts):
    urls = [(f"{BASE_URL}/", "weekly", "1.0"), (f"{BASE_URL}/blog/", "weekly", "0.9")]
    urls += [(f"{BASE_URL}/blog/{p['slug']}.html", "monthly", "0.8") for p in posts]
    entries = "".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>\n"
        for loc, freq, pri in urls
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}</urlset>\n"
    )
    print("Generated sitemap.xml")


def main():
    posts, drafts = load_posts()
    for name in drafts:
        print(f"Skipped draft (no frontmatter): {name}")

    all_cards = "\n".join(render_card(p) for p in posts)
    inject(ROOT / "blog" / "index.html", "blog:cards", all_cards)
    inject(ROOT / "blog" / "index.html", "blog:filters", render_filters(posts))
    print(f"Updated blog/index.html ({len(posts)} posts)")

    latest = "\n".join(render_card(p) for p in posts[:HOME_POST_COUNT])
    inject(ROOT / "index.html", "blog:latest", latest)
    print(f"Updated index.html (latest {min(HOME_POST_COUNT, len(posts))} posts)")

    write_sitemap(posts)


if __name__ == "__main__":
    main()
