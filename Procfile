release: python manage.py migrate
web: daphne leech.asgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery -A leech.celery worker -l info
celerybeat: celery -A leech beat -l INFO 
celeryworker2: celery -A leech.celery worker & celery -A leech beat -l INFO & wait -n