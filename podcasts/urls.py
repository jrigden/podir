from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^category/(?P<slug>[\w-]+)', views.category, name='category_detail'),
    url(r'^stats', views.stats, name='stats'),
    url(r'^', views.index, name='index'),
]
