import datetime

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from home.models import Social, Copyright, AboutFooter, Logo, \
    Page, BlogPageMediaItem, AboutPageContactItem, MediaItem

register = template.Library()


@register.simple_tag(takes_context=True)
def test_tag(context):
    import pdb; pdb.set_trace()
    return {
        'request': context['request']
    }


# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


# Site wide get root method
@register.assignment_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


# Contact Item populate
@register.inclusion_tag('home/tags/contact_item.html', takes_context=True)
def contact_item(context, item):
    self = context.get('self')
    contact_page = item.link_page
    return {
        'contact_page': contact_page,
        'item': item,
        'request': context['request'],
    }


# Blog hero area, to display the blog index image and title
@register.inclusion_tag('home/tags/index_image.html', takes_context=True)
def index_image(context):
    self = context.get('self')
    if self.content_type.model == 'blogindexpage':
        blog_index = self
    elif self.content_type.model == 'aboutpage':
        blog_index = self
    elif self.content_type.model == 'seasonpage':
        blog_index = self
    else:
        blog_index = self.get_parent().specific
    return {
        'blog_index': blog_index,
        'request': context['request'],
    }


def blog_item(context, blog):
    self = context.get('self')
    try:
        media_item = BlogPageMediaItem.objects.get(page=blog)
    except ObjectDoesNotExist:
        media_item = None
    try:
        media_item = MediaItem.objects.get(page=blog)
    except ObjectDoesNotExist:
        media_item = None
    supported_sites = None
    if media_item:
        if media_item.link_external:
            url_split = media_item.link_external.split('.')
            supported_sites = []
            if 'youtube' in url_split:
                supported_sites.append('youtube')
            elif 'soundcloud' in url_split:
                supported_sites.append('soundcloud')
            elif 'vimeo' in url_split:
                supported_sites.append('vimeo')
    return {
        'blog': blog,
        'media_item': media_item,
        'supported_sites': supported_sites,
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/blog_index_item.html', takes_context=True)
def blog_index_item(context, blog):
    return blog_item(context, blog)


@register.inclusion_tag('home/tags/blog_hero_item.html', takes_context=True)
def blog_hero_item(context, blog):
    return blog_item(context, blog)


@register.inclusion_tag('home/tags/venue_index_item.html', takes_context=True)
def venue_index_item(context, venue):
    address = venue.venue_details.address.split(',')
    short_address = address[0] + ',' + address[1]
    open_hours = venue.open_hours
    if len(open_hours) > 1:
        open_days = str(len(open_hours))
    else:
        open_days = False
    return {
        'address': short_address,
        'open_days': open_days,
        'venue': venue,
        'request': context['request']
    }


# Breadcrumb tag
@register.inclusion_tag('home/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=1)
    return {
        'ancestors': ancestors,
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/index_pagination.html', takes_context=True)
def index_pagination(context):
    paginator = context['paginator']
    render_nums = []
    for num in range(1, paginator.paginator.num_pages + 1):
        if -1 <= paginator.number - num <= 1:
            render_nums.append(num)
    return {
        'paginator': paginator,
        'pages': render_nums,
        'request': context['request'],
    }


@register.filter
def openhour_time(value):
    hour = int(value[:2])
    minute = int(value[2:])
    date = datetime.time(hour, minute)
    return date.strftime("%H:%M")


# Social Snippet
@register.inclusion_tag('home/tags/base/social.html', takes_context=True)
def social(context):
    return {
        'socials': Social.objects.select_related('page'),
        'request': context['request'],
    }


# Copyright Snippet
@register.inclusion_tag('home/tags/base/copyright.html', takes_context=True)
def copyright_snippet(context):
    return {
        'copyright': Copyright.objects.select_related('page'),
        'request': context['request'],
    }


# Footer Snippet
@register.inclusion_tag('home/tags/base/footer_about.html', takes_context=True)
def aboutfooter(context):
    return {
        'footer': AboutFooter.objects.select_related('page'),
        'request': context['request'],
    }


# Logo Snippet
@register.inclusion_tag('home/tags/base/logo.html', takes_context=True)
def logo(context):
    return {
        'logos': Logo.objects.select_related('page'),
        'request': context['request'],
    }
