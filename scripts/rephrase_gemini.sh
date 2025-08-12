#!/bin/bash

usage() {
  echo "Usage: $0 <text_to_rephrase> [tone] [enable_log]"
  echo "  <text_to_rephrase>: Text to be rephrased"
  echo "  [tone]: Rephrasing tone, default is neutral"
  echo "  [enable_log]: Enable logging, true/1/yes/log to enable, default is enabled"
  exit 1
}

if [ $# -lt 1 ]; then
  usage
fi

text="$1"
tone="${2:-neutral}"
enable_log=true
if [ $# -ge 3 ]; then
  val=$(echo "$3" | tr '[:upper:]' '[:lower:]')
  case "$val" in
    true|1|yes|log) enable_log=true ;;
    false|0|no) enable_log=false ;;
    *) enable_log=true ;;
  esac
fi

cred_file="$(dirname "$0")/../credentials/gemini.json"
if [ ! -f "$cred_file" ]; then
  echo "Error: Credentials file not found at $cred_file"
  exit 1
fi

API_KEY=$(jq -r '.api_key' "$cred_file")
if [ -z "$API_KEY" ] || [ "$API_KEY" == "null" ]; then
  echo "Error: api_key not found in $cred_file"
  exit 1
fi


read -r -d '' payload <<EOF
{
  "contents": [
    {
      "parts": [
        {
          "text": "Please rephrase the following text in a $tone tone. ONLY reply with the rephrased text, no explanations or extra commentary: \\n$text"
        }
      ],
      "role": "user"
    }
  ]
}
EOF

response=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$payload")

rephrased_text=$(echo "$response" | jq -r '.candidates[0].content.parts[0].text')

if [ -z "$rephrased_text" ] || [ "$rephrased_text" == "null" ]; then
  echo "Error: Failed to get rephrased text from response"
  exit 1
fi

echo "$rephrased_text"

log_io() {
  if [ "$enable_log" = true ]; then
    log_dir="$(dirname "$0")/../log"
    mkdir -p "$log_dir"
    logfile="$log_dir/log.txt"
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    {
      echo "$now - INPUT:"
      echo "$text"
      echo "$now - OUTPUT:"
      echo "$rephrased_text"
      echo "----------------------------------------"
    } >> "$logfile"
  fi
}

log_io