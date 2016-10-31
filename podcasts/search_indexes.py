import re
from haystack import indexes
from podcasts.models import Category, Episode, Podcast


class EpisodeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', boost=1.0)
    subtitle = indexes.CharField(model_attr='subtitle', boost=0.75)
    summary = indexes.CharField(model_attr='summary',boost=0.25)

    def get_model(self):
        return Episode

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
        #return self.get_model().objects.filter(podcast__active=True)
