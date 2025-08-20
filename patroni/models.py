from django.db import models


# Create your models here.
class Server(models.Model):
    host_ip = models.CharField(max_length=15)
    username = models.CharField(max_length=15)
    password = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}@{}".format(self.username, self.host_ip)
