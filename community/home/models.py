from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, SET_DEFAULT
import datetime 


# Create your models here.

class Event(models.Model):
    organizer = models.ForeignKey(User,on_delete=CASCADE)
    event_title = models.CharField(max_length=30,default='Event Title')
    event_subtitle = models.CharField(max_length=100,blank=True)
    location = models.CharField(max_length=50,blank=True)
    date = models.DateTimeField(blank=True)
    time = models.TimeField(default=datetime.time(10, 00, 00))
    description = models.TextField(blank=True)

    def __str__(self):
        return self.event_title

    