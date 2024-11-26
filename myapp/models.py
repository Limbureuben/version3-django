from unicodedata import category
from django.db import models
from datetime import date
import uuid
from django.contrib.auth.models import AbstractUser
from pyexpat import model
from django.contrib.auth.models import User

    

# class Weather(models.Model):
#     temperature = models.FloatField()
#     humidity = models.FloatField()
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
    
class Files(models.Model):
    file = models.FileField(upload_to="uploads/", null=True, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=55)

class Event(models.Model):
    event_username = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField(default=date.today)
    event_location = models.CharField(max_length=255)
    # event_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events', null=True)  # Link to Category
    event_category = models.CharField(max_length=100, null=False, default='default_category')
    # image = models.ImageField(upload_to='event_image/', null=True, blank=True)
    
    def __str__(self):
        return self.event_name

class EventApplication(models.Model):
    # id = models.AutoField(primary_key=True)
    application_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=[("Attendee", "Attendee"), ("Speaker", "Speaker"), ("interested", "Interested")])
    event = models.ForeignKey(Event, related_name='applications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.event.event_name}"
    
class RegisterBook(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    publication_date = models.DateField(auto_now=True)
    