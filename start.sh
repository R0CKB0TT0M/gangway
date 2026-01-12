#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

"$(dirname "$0")/venv/bin/python3" "$(dirname "$0")/main.py"
