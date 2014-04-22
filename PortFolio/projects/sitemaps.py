from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from django.db.models import Min, Max
from projects.models import Project

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 1.
    changefreq = 'weekly'

    def items(self):
        return ['projects.views.home']

    def location(self, item):
        return reverse(item)

class YearViewSitemap(sitemaps.Sitemap):
    priority_min = .6
    priority_max = .9
    
    changefreq = 'weekly'

    def items(self):
        year_min_max = Project.objects.aggregate(Min('year'), Max('year'))
        
        self.year_min = year_min_max["year__min"]
        self.year_max = year_min_max["year__max"]
        
        if self.year_min == self.year_max:
            self.year_min = None
            self.year_max = None

        return Project.objects.all().values('year').distinct()

    def location(self, item):
        return reverse('projects.views.show_projects_year', args=[item["year"],])

    def priority(self, item):
        if not self.year_min or not self.year_max:
            return 0.7

        return self.priority_min + (self.priority_max - self.priority_min) * (item["year"] - self.year_min) / (self.year_max - self.year_min)

class ProjectViewSitemap(sitemaps.Sitemap):
    priority_min = .4
    priority_max = .8
    
    year_min = None
    year_max = None

    changefreq = 'weekly'

    def items(self):
        year_min_max = Project.objects.aggregate(Min('year'), Max('year'))
        
        self.year_min = year_min_max["year__min"]
        self.year_max = year_min_max["year__max"]
        
        if self.year_min == self.year_max:
            self.year_min = None
            self.year_max = None

        return Project.objects.filter(private=False)

    def location(self, item):
        return item.get_absolute_url()

    def priority(self, item):
        if not self.year_min or not self.year_max or not item.year:
            return 0.5

        return self.priority_min + (self.priority_max - self.priority_min) * (item.year - self.year_min) / (self.year_max - self.year_min)

    def lastmod(self, item):
        return item.modified

