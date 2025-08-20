from django.urls import path
from . import views

app_name = "patroni"

urlpatterns = [
    path('', views.patroni),
    path('patroni', views.patroni),
    path('cluster', views.cluster, name="cluster"),
    path('restart', views.restart, name="restart"),
    path('switchover', views.switchover, name="switchover"),
    path('history', views.history),
    path('config', views.config),
    path('server', views.server, name='server'),
    path('add_server', views.add_server, name='add_server'),
    path('delete_server', views.delete_server, name='delete_server'),
]
