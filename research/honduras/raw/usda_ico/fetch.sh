#!/bin/bash
# usage: fetch.sh URL OUTFILE  -> logs to FETCH_LOG.md, prints http code
url="$1"; out="$2"
host=$(echo "$url" | sed -E 's#https?://([^/]+).*#\1#')
last=/tmp/claude-0/-home-user-procafe/c2981ec8-bab5-570c-97d8-be6dc45e657c/scratchpad/last_$host
rm -f "$out"; [ -f "$last" ] && sleep 1
touch "$last"
res=$(curl -sS -L -m 60 -A "Mozilla/5.0" -o "$out" -w '%{http_code} %{url_effective} %{content_type}' "$url" 2>/tmp/claude-0/-home-user-procafe/c2981ec8-bab5-570c-97d8-be6dc45e657c/scratchpad/err)
err=$(head -c 150 /tmp/claude-0/-home-user-procafe/c2981ec8-bab5-570c-97d8-be6dc45e657c/scratchpad/err | tr '\n|' '  ')
code=${res%% *}
size=$(stat -c %s "$out" 2>/dev/null || echo 0)
echo "| $(date -u +%H:%M:%S) | $url | $code | $(echo "$res" | cut -d' ' -f2) | $(echo "$res" | cut -d' ' -f3-) | $size | $err |" >> FETCH_LOG.md
echo "$code $size $err"
