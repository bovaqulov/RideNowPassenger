# ===========================================
# 1. Asosiy imij
# ===========================================
FROM python:3.10-alpine

# Ishchi katalog
WORKDIR /app

# Python konfiguratsiyasi
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ===========================================
# 2. Build tools va PostgreSQL uchun kerakli kutubxonalar
# ===========================================
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    bash

# ===========================================
# 3. Kutubxonalarni o‘rnatish
# ===========================================
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# ===========================================
# 4. Loyihani ko‘chirish
# ===========================================
COPY . .

# ===========================================
# 5. Ishga tushirish jarayonlari (hammasi shu yerda)
# ===========================================
# ⬇️ collectstatic, migrate, custom commands, va gunicorn bir joyda
CMD \
    echo "📦 Migratsiyalarni yaratish..." && \
    python manage.py makemigrations --noinput && \
    echo "📂 Migratsiyalarni qo‘llash..." && \
    python manage.py migrate --noinput && \
    echo "🎨 Statik fayllarni yig‘ish..." && \
    python manage.py collectstatic --noinput && \
    echo "💬 Custom komandalar ishga tushmoqda..." && \
    (python manage.py set_message || true) && \
    (python manage.py createsuper || true) && \
    echo "🚀 Gunicorn ishga tushmoqda..." && \
    gunicorn ridebot_passenger.wsgi:application --bind 0.0.0.0:8000 --workers 3
