#!/bin/bash

git init

git add .

git commit -m "Update $(date '+%Y-%m-%d %H:%M:%S')"

git push -u origin development