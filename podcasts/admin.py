from django.contrib import admin

# Register your models here.

from .models import Category, Episode, Podcast

admin.site.register(Category)
admin.site.register(Episode)
admin.site.register(Podcast)
