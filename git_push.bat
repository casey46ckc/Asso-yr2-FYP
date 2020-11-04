set /P message=Enter the commited message for pushing: 
git pull
git add .
git commit -m "%message%"
git push
PAUSE
