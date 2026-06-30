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

set -euo pipefail

# Run from the repo root no matter where the script is called from.
cd "$(dirname "$0")/.."

BASE_URL="${BASE_URL:-https://www.matthewlbrown.com}"

build_one() {
  local src="$1"
  local slug
  slug="$(basename "${src%.md}")"
  local out="blog/${slug}.html"

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

generate_sitemap() {
  local sitemap="sitemap.xml"
  local base_url="https://www.matthewlbrown.com"

  cat > "$sitemap" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${base_url}/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>${base_url}/blog/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
EOF

  for f in blog/_posts/*.md; do
    local slug
    slug="$(basename "${f%.md}")"
    cat >> "$sitemap" <<EOF
  <url>
    <loc>${base_url}/blog/${slug}.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
EOF
  done

  echo "</urlset>" >> "$sitemap"
  echo "Generated $sitemap"
}

if [ "$#" -ge 1 ]; then
  build_one "$1"
else
  for f in blog/_posts/*.md; do
    build_one "$f"
  done
fi

generate_sitemap
