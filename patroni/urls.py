from django.urls import path
from . import views

urlpatterns = [
    path('', views.patroni_view),
]