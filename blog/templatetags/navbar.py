from django import template
from home.models import HomePage
from blog.models import BlogIndexPage, BlogSearchPage

register = template.Library()

@register.inclusion_tag('navbar.html')
def navbar():

    home_page = HomePage.objects.get()

    ix_pages = home_page.get_children().type(BlogIndexPage).not_type(BlogSearchPage)

    return {'ix_pages': ix_pages, 'home_page': home_page}