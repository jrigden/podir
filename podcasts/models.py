from django.db import models

# Create your models here.


class Category(models.Model):
    slug = models.CharField(unique=True, max_length=30)
    title = models.CharField(unique=True, max_length=30)

    def __str__(self):
            return self.title


class Podcast(models.Model):
    active = models.BooleanField(db_index=True, default=True)
    added = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category)
    fail_count = models.IntegerField(default=0)
    feed_url = models.URLField(unique=True)
    last_episode = models.DateTimeField(db_index=True, null=True, blank=True)
    published = models.DateTimeField(db_index=True, null=True, blank=True)
    site_url = models.URLField()
    subtitle = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=200)

    def __str__(self):
            return self.title


class Episode(models.Model):
    enclosure_url = models.URLField(db_index=True, unique=True, default=None, max_length=500)
    guid = models.URLField(db_index=True, default=None, max_length=500, unique=True)
    subtitle = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    post_url = models.URLField(max_length=500)
    published = models.DateTimeField(db_index=True, default=None)
    title = models.CharField(max_length=200)

    def __str__(self):
            return self.title
