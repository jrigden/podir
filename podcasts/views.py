from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


# Create your views here.

from .models import Category, Episode, Podcast


def index(request):
    categories = Category.objects.all().order_by('title')
    template = loader.get_template('podcasts/index.html')
    context = {
        'categories': categories,
    }
    return HttpResponse(template.render(context, request))

def category(request, slug):
    template = loader.get_template('podcasts/category.html')
    response = "You're looking at the results of question %s."
    category = get_object_or_404(Category, slug=slug)
    podcasts = Podcast.objects.filter(active=True, categories=category).order_by('?')
    context = {
        'category': category,
        'podcasts': podcasts,
    }
    return HttpResponse(template.render(context, request))

def stats(request):
    episode_count = Episode.objects.count()
    podcast_count = Podcast.objects.count()
    active_podcast_count = Podcast.objects.filter(active=True).count()

    template = loader.get_template('podcasts/stats.html')
    context = {
        'active_podcast_count': active_podcast_count,
        'episode_count': episode_count,
        'podcast_count': podcast_count,
    }
    return HttpResponse(template.render(context, request))
