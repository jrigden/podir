# -*- coding: utf-8 -*-
from random import shuffle
import datetime
import logging
import os
import pytz
import sys

from bs4 import BeautifulSoup
from celery import Celery
from pyPodcastParser.Podcast import Podcast as PodcastParser

import coloredlogs
import django
import requests
import requests_cache

# Settings
DAYS_TO_EXPIRE = 90
FAIL_LIMIT = 3
REDIS_DB_ID = 5
TIMEOUT_LIMIT = 2

# Celery Setup
BROKER_URL = 'redis://localhost:6379/' + str(REDIS_DB_ID)
app = Celery('tasks', broker=BROKER_URL)

# Django Setup
sys.path.append("/home/jason/Code/podir/podir/podir/")
os.environ['DJANGO_SETTINGS_MODULE'] = 'podir.settings'
django.setup()

# Loggin Setup
LOG_FORMAT = '%(asctime)s  %(levelname)-8s  %(message)s'
LOG_DATE = "%Y-%m-%d %H:%M:%S"
LOG_STYLE = dict(
    debug=dict(color='cyan', bold=True),
    info=dict(color='green', bold=True),
    verbose=dict(color='white'),
    warning=dict(color='yellow', bold=True),
    error=dict(color='red', bold=True),
    critical=dict(color='magenta', bold=True))

logger = logging.getLogger('logging_template')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FORMAT, LOG_DATE)

fileHander = logging.FileHandler('podir_loader.log')
fileHander.setLevel(logging.INFO)
fileHander.setFormatter(formatter)
logger.addHandler(fileHander)

coloredlogs.install(level='DEBUG', fmt=LOG_FORMAT,
                    datefmt=LOG_DATE, level_styles=LOG_STYLE)

# Requests Cache Setup
requests_cache.install_cache('test_cache', backend='sqlite', expire_after=300000)

# Models Setup
from podcasts.models import Category, Episode, Podcast

# Catergory Funcs
def clean_categories(list_of_categories):
    print(list_of_categories)
    cleaned_set_of_categories = set()
    for category in list_of_categories:
        if category is None:
            category = ""
        category = category.lower()
        category = category.strip()
        cleaned_set_of_categories.add(category)
    cleaned_list_of_categories = list(cleaned_set_of_categories)
    #print(cleaned_list_of_categories)
    return cleaned_list_of_categories

def create_or_get_categories(categories):
    saved_categories = []
    for category in categories:
        saved_category = create_or_get_category(category)
        saved_categories.append(saved_category)
    return saved_categories

def create_or_get_category(category_title):
    category_slug = django.utils.text.slugify(category_title, allow_unicode=True)
    category, created = Category.objects.get_or_create(slug=category_slug, title=category_title)
    category.save()
    return category


# Episode Funcs
def create_episode(episode_info, podcast):
    if episode_info.enclosure_url is None:
        logger.info("Episode does not have enclosure_url. Podcact ID: " + str(podcast.id))
        return False
    if episode_info.title is None:
        logger.info("Episode does not have a title. Podcact ID: " + str(podcast.id))
        return False

    logger.info("Attempting to create episode with enclosure_url: " + episode_info.enclosure_url)
    episode = Episode()

    episode.enclosure_url = episode_info.enclosure_url[:499]
    episode.guid = episode_info.guid

    if episode_info.link is None:
        episode.post_url = podcast.site_url
    elif episode_info.link.endswith(".mp3"):
        episode.post_url = podcast.site_url
    else:
        episode.post_url = episode_info.link

    episode.subtitle = long_text_cleaner(episode_info.itunes_subtitle)
    episode.summary = long_text_cleaner(episode_info.itunes_summary)

    episode.podcast = podcast
    if episode_info.date_time is None:
        episode.published  = None
    else:
        episode.published = pytz.utc.localize(episode_info.date_time)
    episode.title = episode_info.title[:199]
    try:
        episode.save()
    except django.db.utils.IntegrityError:
        logger.info("Duplicate episode with enclosure_url: " + episode_info.enclosure_url)
        return False
    logger.info("Episode created with ID: " + str(episode.id))

# Podcast Funcs
@app.task
def add_podcast(submitted_url):
    if Podcast.objects.filter(feed_url=submitted_url).exists():
        logger.info("URL is already in DB: " + submitted_url)
        return False

    try:
        response = requests.get(submitted_url, timeout=TIMEOUT_LIMIT)
        logger.info("Valid URL: " + submitted_url)
    except:
        logger.info("Invalid URL: " + submitted_url)
        return False

    if Podcast.objects.filter(feed_url=response.url).exists():
        logger.info("Resolved URL is already in DB: " + response.url)
        return False

    parsedPodcast = PodcastParser(response.content)
    if not parsedPodcast.is_valid_podcast:
        logger.info("URL is invalid podcast: " + response.url)
        return False
    else:
        logger.info("URL is valid podcast: " + response.url)

    new_podcast = Podcast(feed_url=response.url)
    new_podcast.save()
    logger.info("Podcast saved with ID: " + str(new_podcast.id))
    return True

@app.task
def update_podcast(podcast_id):
    logger.info("Updating Podcast ID: " + str(podcast_id))
    podcast = Podcast.objects.get(pk=podcast_id)

    try:
        response = requests.get(podcast.feed_url, timeout=TIMEOUT_LIMIT)
    except:
        report_podcast_failure(podcast_id)
        return False
    parsedPodcast = PodcastParser(response.content)
    if not parsedPodcast.is_valid_podcast:
        report_podcast_failure(podcast_id)
        return False


    if parsedPodcast.title is None:
        report_podcast_failure(podcast_id)
        return False

    if parsedPodcast.itunes_new_feed_url:
        logger.info("Updating Feed URL for ID: " + str(podcast_id))
        podcast.feed_url = parsedPodcast.itunes_new_feed_url
    else:
        podcast.feed_url = response.url

    categories = clean_categories(parsedPodcast.itunes_categories)
    saved_categories = create_or_get_categories(categories)
    podcast.categories = saved_categories

    if parsedPodcast.date_time is None:
        podcast.published = None
    else:
        podcast.published = pytz.utc.localize(parsedPodcast.date_time)

    podcast.site_url = parsedPodcast.link

    podcast.subtitle = long_text_cleaner(parsedPodcast.subtitle)
    podcast.summary = long_text_cleaner(parsedPodcast.summary)

    podcast.title = parsedPodcast.title[:199]

    podcast.fail_count = 0

    try:
        podcast.save()
    except django.db.utils.IntegrityError:
        logger.info("Updated Podcast Has Duplicate Feed URL: " + str(podcast_id))
        report_podcast_failure(podcast_id)

    for episode in parsedPodcast.items:
        create_episode(episode, podcast)
    podcast_active_check(podcast_id)

@app.task
def podcast_active_check(podcast_id):
    logger.info("Checking active status of Podcast: " + str(podcast_id))
    expiration_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=DAYS_TO_EXPIRE)
    #try:
    podcast = Podcast.objects.get(pk=podcast_id)
    #print(podcast)

    #except:
    #    return
    episodes = Episode.objects.filter(podcast=podcast).order_by('-published')
    #print(episodes)
    if len(episodes) == 0:
        logger.info("Podcast has no episodes and is inactive: " + str(podcast.id))
        podcast.active = False
        podcast.save()
        return False
    #print(str(len(episodes)))
    #print(episodes[0].published)
    if expiration_date > episodes[0].published:
        logger.info("Podcast is inactive: " + str(podcast.id))
        podcast.active = False
        podcast.save()
        return False
    else:
        logger.info("Podcast is active: " + str(podcast.id))
        podcast.active = True
        podcast.save()
        return True

def report_podcast_failure(podcast_id):
    try:
        podcast = Podcast.objects.get(pk=podcast_id)
    except:
        return
    podcast.fail_count += 1
    podcast.save()
    if podcast.fail_count > FAIL_LIMIT:
        podcast.delete()

def update_all_podcasts():
    podcasts = Podcast.objects.all().order_by('?')
    for podcast in podcasts:
        logger.info("Requesting Update of Podcast ID: " + str(podcast.id))
        update_podcast.delay(podcast.id)

# Utilities
def long_text_cleaner(long_text):
    cleaned_text = ""
    if long_text is None:
        return cleaned_text
    cleaned_text = BeautifulSoup(long_text).text
    cleaned_text = truncate_long_words(cleaned_text)
    return cleaned_text

def truncate_long_words(submitted_text):
    try:
        words = submitted_text.split()
    except AttributeError:
        return ""
    for i, word in enumerate(words):
        words[i] = words[i][:46]
    result = ' '.join(words)
    return result





########################################################

@app.task
def add(x, y):
    return x + y
