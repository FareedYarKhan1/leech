# leech
#Commands to locally run
#sudo apt-get install chromium-chromedriver

1. pip install -r requirements.txt
2. python manage.py runserver
celery -A leech purge
3. celery -A leech.celery worker --pool=solo -l info
4. celery -A leech beat -l info

# Testing
#single task
#multiple task
##monitoring
#1 time run
#main.csv
#newlinks.csv
#keyword testing
#check link not appear outside
#javascript problem
#tasknumber assign
#logout and login to check notification
