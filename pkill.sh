
ps -ef | grep -i chromedriver | grep tcoleman | awk '{print $2}' | xargs kill
ps -ef | grep -i chromium-browser | grep tcoleman | awk '{print $2}' | xargs kill
ps -ef | grep -i webdriver | grep tcoleman | awk '{print $2}' | xargs kill
ps -ef | grep -i xvfb | grep tcoleman | awk '{print $2}' | xargs kill

