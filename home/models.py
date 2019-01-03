from django.db import models
from django.utils import timezone

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel

from blog.models import BlogPage

import datetime


class HomePage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Add additional context here

        context['main_articles'] = BlogPage.objects.filter(
            editors_pick=True,
            publication_date__gte=(
                timezone.now() - datetime.timedelta(days=30))
        ).order_by('-views')[:3]

        context['latest'] = BlogPage.objects.order_by('-publication_date')[:5]

        context['recent_popular'] = BlogPage.objects.filter(publication_date__gte=(
            timezone.now() - datetime.timedelta(days=30))).order_by('-views')[:5]

        context['hot'] = BlogPage.objects.filter(hot_news=True).live().last()

        context['editors_picks'] = BlogPage.objects.filter(
            editors_pick=True).live().order_by('-first_published_at')[:3]
            
        context['popular'] = BlogPage.objects.live().order_by('-views')[:5]

        return context
