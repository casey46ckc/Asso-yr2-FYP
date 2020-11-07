#!/bin/bash
echo -n "Leave the commit message here: "
read -r message
git pull
git add .
git commit -m $message
git push
