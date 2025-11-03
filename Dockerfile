FROM python:3.10-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# PostgreSQL va build tools
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

COPY requirements.txt .

# gunicorn ham o‘rnatiladi
RUN pip install --upgrade pip && pip install -r --no-cache requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py set_message || true
RUN python manage.py createsuper || true

# Gunicorn orqali ishga tushirish
CMD ["gunicorn", "ridebot_passenger.wsgi:application", "--bind", "0.0.0.0:8000"]
