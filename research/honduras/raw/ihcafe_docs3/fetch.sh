#!/bin/bash
# Usage: fetch.sh NNN URL  -> downloads, logs to FETCH_LOG.tsv
cd "$(dirname "$0")"
n=$1; url=$2
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
name=$(echo "$url" | sed -E 's#^https?://##; s#[^A-Za-z0-9._-]#_#g' | cut -c1-90)
tmp=$(mktemp)
for t in 1 2; do
  out=$(curl -sS -L -A "$UA" --max-time 60 -o "$tmp" -w '%{http_code}\t%{url_effective}\t%{size_download}\t%{content_type}' "$url" 2>&1) && break
done
code=$(echo "$out" | cut -f1)
ct=$(echo "$out" | cut -f4)
ext=html; case "$ct" in *pdf*) ext=pdf;; esac
head -c5 "$tmp" | grep -q '%PDF' && ext=pdf
f="${n}_${name}.${ext}"
if [ -s "$tmp" ]; then mv "$tmp" "$f"; else rm -f "$tmp"; f="-"; fi
printf '%s\t%s\t%s\t%s\n' "$n" "$url" "$out" "$f" >> FETCH_LOG.tsv
echo "$n $out $f"
