#!/bin/bash
FILE=Pipfile
CMD1="cd $PWD;pipenv run python3 main.py"
CMD2="cd $PWD;ngrok http 5000"
function pause(){
    read -p "$*"
}
if [ -f "$FILE" ]; then
    echo "$FILE exists."
    pipenv --rm
else
    echo "$FILE not exists."
fi
pipenv install --three python-telegram-bot flask gunicorn requests
osascript -e "tell app \"Terminal\" to do script \"$CMD1\""
osascript -e "tell app \"Terminal\" to do script \"$CMD2\""
pause "Press [Enter] key to continue..."
echo -n "Leave the link here: "
read -r link
open -n "https://api.telegram.org/bot1245594409:AAFrCtnQn6Och-qrTvaIzh_7W6hc8jF0iVE/setWebhook?url=$link/hook"
