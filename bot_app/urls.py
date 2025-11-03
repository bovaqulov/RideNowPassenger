from django.urls import path

from bot_app import views


urlpatterns = [
    path("webhook/", views.telegram_passenger_bot),
    path("webhook/deploy/", views.telegram_passenger_bot),
    path("set_web/", views.set_web),
    path("set_web/deploy/", views.set_deploy),
]