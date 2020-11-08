# Asso-yr2-FYP
HKUspace Engineering Yr2 (CS theme) FYP

----------------------------------------------------------------------

For Developers

Prerequisites installation before running the Spacebot
1.Python 3.6 up
2.pipenv
3.ngrok (install in linux/mac OS, put the executable file in the same directory for windowsOS)


Steps to open the test server for testing
1. Extract the project files in to certain directory
Run the following code under the project directory using terminal
2. pipenv install --three python-telegram-bot flask gunicorn requests)
3. pipenv run python3 main.py (for macOS / Linux, may vary if the path is different from default for windows OS)
4. open another terminal and run the following command: "ngrok http 5000" and then
copy the https link shown in the ngrok terminal.
5. put the link and add"/hook" at the end of the link to the attribute "WEBHOOK_URL" under the config.ini file.
6. open the browser and type in the following link:
https://api.telegram.org/bot{$token}/setWebhook?url={$webhook_url}
where {$token} is the "ACCESS_TOKEN" you received when you build the telegram chatbot and {$webhook_url} is the link you just stored in config.ini file in the previous step

*For convienience, you may skip the steps from 2 to 6 and use serverinit.bat for windows OS and serverinit.bash for the mac OS to open the server

----------------------------------------------------------------------

For user experience

Prerequisites installation
1.Telegram app for mobile/ Telegram app for desktoop


Steps to communicate with the Spacebot
1. Type the tag name “fypspacebot” in the search bar and select it
2. Click the start button

Questions you may ask/ valid input messages
1. hi/hello/bye     
2. Tell me the contact of (KEC/Kowloon east campus/IEC/island east campus/fortress tower centre/ fortress tower center)?
3. Where is the (library/lib/libra/common room/大com/細com/com rm/study room/discussion room/computer lab)?
4. Which floor is (library/lib/libra/common room/大com/細com/com rm/study room/discussion room/computer lab)?

Remarks:
**Punctuations are considered as skipper in Olami and they are not considered in processing, therefore, users are not necessary to add a “?”. The chatbot recognize it’s a question from the “wh” keywords.**