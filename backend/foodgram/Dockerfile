FROM python:3.8.5
WORKDIR /code
COPY ./backend/foodgram/requirements.txt .
RUN pip install -r ./requirements.txt
COPY . .
RUN python manage.py shell < clean_database.py
RUN python manage.py loaddata dump.json
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 
