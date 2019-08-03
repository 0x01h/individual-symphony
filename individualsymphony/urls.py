import logging

from django.urls import path
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemaps import StaticViewSitemap


sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('language', views.language, name='language'),
    path('evaluate', views.evaluate, name='evaluate'),
    path('feedback', views.feedback, name='feedback'),
    path('song_genre_suggestion', views.song_genre_suggestion, name='song_genre_suggestion'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
    name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('whitepaper', views.whitepaper, name='whitepaper'),
    path('references', views.references, name='references'),
    path('changelog', views.changelog, name='changelog'),
    path('contact', views.contact, name='contact'),
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\n\nSitemap: https://individualsymphony.com/sitemap.xml", content_type="text/plain")),
)
    
