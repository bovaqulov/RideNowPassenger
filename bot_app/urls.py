from django.urls import path

from bot_app import views


urlpatterns = [
    path("webhook/", views.telegram_passenger_bot),
    path("set_web/", views.set_web),
]