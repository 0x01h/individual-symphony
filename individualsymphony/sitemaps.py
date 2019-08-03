from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'
    i18n = True

    def items(self):
        return ['home', 'about', 'changelog', 'contact', 'references', 'whitepaper']

    def location(self, item):
        return reverse(item)