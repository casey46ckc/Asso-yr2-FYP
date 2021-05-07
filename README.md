# Asso-yr2-FYP
HKUspace Engineering Yr2 (CS theme) FYP

For Application Developer

----------------------------------------------------------------------

For Administrator

You can either choose deploy directly to Heroku server or synchronise the application with a GitHub project.

Method 1: deploy by synchronisation of GitHub repository
Prerequisites deploy the Spacebot application to Heroku Server by synchronisation of GitHub repository
1. GitHub Desktop or Git
	You can find the installation package via Official Website: 
	GitHub Desktop: https://desktop.GitHub.com/
	Git: https://git-scm.com/downloads
2. Establish the linkaage between GitHub repository and Heroku application
	Steps to establish the linkaage between GitHub repository and Heroku application:
	1. login to your Heroku account via browser in Heroku Dashboard page.
	2. go to the app’s “Deploy” tab on Heroku Dashboard and select the GitHub pane. 
	If you haven’t connected your Heroku and GitHub accounts, you will be prompted to complete the GitHub OAuth flow. 
	Heroku needs access to help you select repos and to be able to register webhooks triggered when you push to GitHub. 
	Once connected, you can select which repo associated with your GitHub account to link to the Heroku app.
	With app and repo connected, you can either manually deploy a specific branch, or select a Git branch that will be auto-deployed whenever it’s pushed to on GitHub.
	
Steps to deploy the application to Heroku server using GitHub Desktop
1. Make sure you the appropriate repository and branch is opened, 
2. Click the "Fetch origin" button to check the consistency. If inconsistency happen, solve the conflict before clicking the "pull" button
3. When you are ready to update, type in the message you want to leave in the "Summary(required)" Text Box, and then click "Commit to master" button
4. Click the "Push" button to update the repository. 


Steps to deploy the application to Heroku server using GitHub CLI
1. Extract the project files in to certain directory
2. Run the following code under the project directory using terminal:
	git pull
	git add.
	git commit -m "The message you want to leave for update"
	git push

*For convienience, you may skip the coding typing in terminal and use git_push.bat for windows OS and git_push.bash for the mac OS to push the update to GitHub repository

Once the repository is successfully updated, it will automatically update the Heroku Application as well

For auto-deploys, you can optionally configure Heroku to wait for continuous integration (like Travis CI) to pass on GitHub. 
With that option enabled, Heroku will only auto-deploy after all GitHub statuses for that commit have succeeded.
Any builds created by the GitHub integration can be tracked in the app’s “Activity” tab and build output for running builds is streamed in Dashboard.

you may refer to the following reference link for more details:
https://devcenter.heroku.com/articles/github-integration

Method 2: deploy by using Heroku CLI

Prerequisites deploy the Spacebot application using Heroku CLI

1. Git
	You can find the installation package via Official Website:
	https://git-scm.com/downloads
2. Heroku CLI
	Windows OS:
	You can find the installation package via Official Website: 
	https://devcenter.heroku.com/articles/heroku-cli#download-and-install
	
	Mac OS:
	You can install it by typing the following command in the terminal:
	brew tap heroku/brew && brew install heroku
	
	
Steps to deploy the application to Heroku server using Heroku CLI
1. Extract the project files in to certain directory
Run the following code under the project directory using terminal
2. heroku login
	The broswer will be prompt and follow the instruction to grant access for you to control the heroku application using the terminal

3. Once you have login to your heroku account, continue to type in the following command using the same terminal:
	git pull
	git add.
	git commit -m "The message you want to leave for update"
	git push heroku main
	
Note that Heroku only deploys code that you push to master or main. Pushing code to another branch of the heroku remote has no effect.
If you want to deploy code to Heroku from a non-main branch of your local repository (for example, testbranch), use the following syntax to ensure it is pushed to the remote’s main branch:\

	git push heroku testbranch:main
	
you may refer to the following reference link for more details:
https://devcenter.heroku.com/articles/git

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