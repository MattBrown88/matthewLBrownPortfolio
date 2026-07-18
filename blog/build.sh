#!/usr/bin/env bash
#
# Build a blog post from Markdown into a site-matching HTML page.
#
# Usage:
#   ./blog/build.sh blog/_posts/my-post.md      # build one post
#   ./blog/build.sh                             # build every post in blog/_posts/
#
# The output file is named after the Markdown file (my-post.md -> my-post.html)
# and written next to the other blog pages in blog/. The slug used for the
# canonical URL is derived from that filename, so name your .md file exactly
# what you want the URL to be.
#
# Posts without YAML frontmatter are treated as drafts: they are not built,
# not listed, and not added to the sitemap.
#
# After building, the blog index (blog/index.html), the home-page blog
# section (index.html), and sitemap.xml are regenerated from frontmatter
# by blog/_generate_listings_and_sitemap.py.

set -euo pipefail

# Run from the repo root no matter where the script is called from.
cd "$(dirname "$0")/.."

BASE_URL="${BASE_URL:-https://www.matthewlbrown.com}"

build_one() {
  local src="$1"
  local slug
  slug="$(basename "${src%.md}")"
  local out="blog/${slug}.html"

  if [ "$(head -1 "$src")" != "---" ]; then
    echo "Skipped draft (no frontmatter): $src"
    return 0
  fi

  pandoc "$src" \
    --from markdown \
    --to html5 \
    --template blog/_template.html \
    --syntax-highlighting=none \
    --wrap=preserve \
    --metadata slug="$slug" \
    --metadata base_url="$BASE_URL" \
    --output "$out"

  echo "Built $out"
}

if [ "$#" -ge 1 ]; then
  build_one "$1"
else
  for f in blog/_posts/*.md; do
    build_one "$f"
  done
fi

# Regenerate blog index cards, home-page latest posts, and sitemap.xml.
python3 blog/_generate_listings_and_sitemap.py
