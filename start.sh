#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

sh -c "cd $(dirname "$0")/frontend && killall next-server || npm run start && npm run start" >> "$(dirname "$0")/output.log" 2>> "$(dirname "$0")/output.log" &

"$(dirname "$0")/venv/bin/python3" "$(dirname "$0")/main.py" >> "$(dirname "$0")/output.log" 2>> "$(dirname "$0")/output.log"
