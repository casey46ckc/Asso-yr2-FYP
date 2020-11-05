set /P message=Leave the commit message here: 
git pull
git add .
git commit -m "%message%"
git push
PAUSE
