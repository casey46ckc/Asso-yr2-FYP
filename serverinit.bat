pipenv install --three python-telegram-bot flask gunicorn requests
start cmd /k pipenv run python main.py
start cmd /k ngrok http 5000
PAUSE
set /P link=Enter the tunnel link for connection:
start "" https://api.telegram.org/bot1245594409:AAFrCtnQn6Och-qrTvaIzh_7W6hc8jF0iVE/setWebhook?url=%link%/hook