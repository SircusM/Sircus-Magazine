#!/bin/sh
# Announce changed pages to Bing and the other IndexNow search engines.
# Usage: sh tools/indexnow.sh https://www.sircusmagazine.com/page-one https://www.sircusmagazine.com/page-two
# The key file /6d2d769848f2cec04e11d95a01223513.txt must stay at the site root; removing it stops the engines accepting submissions.
KEY=6d2d769848f2cec04e11d95a01223513
HOST=www.sircusmagazine.com
[ $# -eq 0 ] && { echo "Give one or more full page addresses."; exit 1; }
LIST=""
for u in "$@"; do LIST="$LIST\"$u\","; done
LIST=${LIST%,}
curl -sS -o /dev/null -w "IndexNow response: %{http_code}\n" -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":[$LIST]}"
