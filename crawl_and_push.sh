#!/bin/sh

python3 storemap.py
git add ./json/
git commit -m "JSON Update $(date '+%Y-%m-%d %H:%M:%S')"
git push origin master
