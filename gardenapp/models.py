from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.contrib.auth.models import Group, Permission
from django.utils import timezone


# Create your models here.






class garden(models.Model) :
    ownerID = models.ForeignKey(User,related_name="owned_gardens" ,on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField()
    longitude =  models.FloatField()
    bio = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    #Need to define where a user is a member / follower of a garden
    members = models.ManyToManyField(User, related_name="followed_gardens" ,blank=True)

class message(models.Model) :
    senderID = models.ForeignKey(User, on_delete=models.CASCADE)
    gardenID = models.ForeignKey(garden, on_delete=models.CASCADE)
    body = models.CharField(max_length=255)
    date_sent = models.DateTimeField(default=timezone.now)



