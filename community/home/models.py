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


class Profile(models.Model):
    name = models.ForeignKey(User,on_delete=CASCADE)
    age = models.IntegerField(default=18)
    gender = models.CharField(default="MALE",max_length=15)
    location = models.CharField(default="Coimbatore",max_length=25)
    role = models.CharField(default="participant",max_length=20)

