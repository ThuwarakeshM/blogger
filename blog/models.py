from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet



class BlogIndexPage(Page):
    intro = models.CharField(max_length=250, blank=True, null=True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None
    
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Context variables here
        all_blogposts = self.get_children().live().order_by('-first_published_at')
        paginator = Paginator(all_blogposts, 10)

        page = request.GET.get('page')
        try:
            blogposts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            blogposts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            blogposts = paginator.page(paginator.num_pages)

        context['blogposts'] = blogposts
        context['hot'] = self.get_children().filter(blogpage__hot_news=True).live().last()
        context['editors_picks'] = self.get_children().filter(blogpage__editors_pick=False).live().order_by('-first_published_at')[:3]
        context['popular'] = self.get_children().live().order_by('-blogpage__views')[:5]

        return context

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogPage(Page):
    publication_date = models.DateField()
    intro = models.CharField(max_length=250, blank=True, null=True)
    body = RichTextField()
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    category = models.ForeignKey('blog.BlogCategory', on_delete=models.SET_NULL, null=True)

    editors_pick = models.BooleanField(default=False)
    hot_news = models.BooleanField(default=False)

    views = models.IntegerField(default=0)

    

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('publication_date'),
            FieldPanel('tags'),
            FieldPanel('category'),
            FieldPanel('editors_pick'),
            FieldPanel('hot_news')
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        #Context Operations
        self.views += 1
        self.save()

        # Extra context variables here
        context['next'] = self.get_next_sibling()
        context['prev'] = self.get_prev_sibling()
        context['hot'] = self.get_siblings().filter(blogpage__hot_news=True).live().last()
        context['editors_picks'] = self.get_siblings().filter(blogpage__editors_pick=False).live().order_by('-first_published_at')[:3]
        context['popular'] = self.get_siblings().live().order_by('-blogpage__views')[:5]

        return context

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]

class BlogIndexPageGalleryImage(Orderable):
    page = ParentalKey(BlogIndexPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]
class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'