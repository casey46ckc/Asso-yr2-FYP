#! /bin/bash
echo Leave the commit message:
read message
git pull
git add .
git commit -m $message
git push
