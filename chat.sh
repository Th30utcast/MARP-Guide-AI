#!/bin/bash
# Chat Service CLI - Colored output

CHAT_URL="http://localhost:8003/chat"

if [ -z "$1" ]; then
    echo "Usage: $0 \"your question\" [top_k]"
    exit 1
fi

QUERY="$1"
TOP_K="${2:-5}"

RESPONSE=$(curl -s -X POST "$CHAT_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"top_k\": $TOP_K}")

echo "$RESPONSE" | python3 -c "
import json, sys

try:
    response_text = sys.stdin.read()
    if not response_text.strip():
        print('\033[1;31m❌ Error:\033[0m No response from server. Is the chat service running?')
        print('\033[0;90mTip: Run \"docker compose ps\" to check service status\033[0m')
        sys.exit(1)

    data = json.loads(response_text)

    if 'detail' in data:
        print('\033[1;31m❌ Error:\033[0m', data['detail'])
        sys.exit(1)

    # Query
    print('\033[1;34m🔍 Query:\033[0m \033[0;37m' + data['query'] + '\033[0m')
    print()

    # Answer
    print('\033[1;36m📝 Answer:\033[0m')
    print('\033[0;37m' + data['answer'] + '\033[0m')
    print()

    # Citations
    if data.get('citations'):
        print('\033[1;33m📚 Citations:\033[0m')
        for i, cite in enumerate(data['citations'], 1):
            print(f'\033[1;32m{i}.\033[0m \033[0;35m{cite[\"title\"]}\033[0m (Page \033[0;33m{cite[\"page\"]}\033[0m)')
            print(f'   \033[0;90m{cite[\"url\"]}\033[0m')
    else:
        print('\033[1;33m📚 Citations:\033[0m \033[0;90mNo citations available\033[0m')

except json.JSONDecodeError as e:
    print('\033[1;31m❌ Error parsing JSON:\033[0m', e)
    print('\033[0;90mRaw response:\033[0m')
    print(response_text)
    sys.exit(1)
except Exception as e:
    print('\033[1;31m❌ Error:\033[0m', e)
    sys.exit(1)
"
