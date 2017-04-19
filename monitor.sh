


while [ 1 ]
do
   date
   top -b -n1 | head -3 | tail -1
   free -m
   printf "xvfb: "
   ps -ef | grep tcoleman | egrep -i xvfb | grep -v grep | wc -l
   printf "webdriver: "
   ps -ef | grep tcoleman | egrep -i webdriver | grep -v grep | wc -l
   printf "chromium-browser: "
   ps -ef | grep tcoleman | egrep -i chromium-browser | grep -v grep | wc -l
   printf "chromedriver: "
   ps -ef | grep tcoleman | egrep -i chromedriver | grep -v grep | wc -l
   printf "\n\n\n\n\n\n"

   sleep 5

done
   
