from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Event)

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_username','event_name', 'event_date', 'event_location', 'event_category')
    search_fields = ('event_name')
    
    
admin.site.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name')
    
admin.site.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'event_id')