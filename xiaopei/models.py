from django.db import models
import django.utils.timezone as timezone

class User(models.Model):
    id = models.AutoField(primary_key=True) 
    age = models.CharField(max_length=50)
    sex = models.CharField(max_length=50)

class Chatting(models.Model):
    id = models.AutoField(primary_key=True) 
    chattingName = models.CharField(max_length=50)
    historyMessage = models.CharField(max_length=32000)

