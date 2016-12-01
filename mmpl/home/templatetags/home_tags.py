from django import template
from django.core.exceptions import ObjectDoesNotExist

from home.models import Social, Copyright, AboutFooter, Logo, HeroItem, \
    Page, BlogPageMediaItem

register = template.Library()


# Site wide get root method
@register.assignment_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


# Hero area get include title, blurb and hero items
@register.inclusion_tag('home/tags/hero_area.html', takes_context=True)
def hero_area(context):
    self = context.get('self')  # Should be onstance of home page.
    hero_items = HeroItem.objects.filter(page=self)
    return {
        'self': self,
        'hero_items': hero_items,
        'request': context['request'],
    }

# Hero area get include title, blurb and hero items
@register.inclusion_tag('home/tags/test_context.html', takes_context=True)
def test_context(context):
    self = context.get('self')  # Should be onstance of home page.
    import pdb; pdb.set_trace()
    return {
        'self': self,
        'request': context['request'],
    }

# Hero area get include title, blurb and hero items
@register.inclusion_tag('home/tags/hero_item.html', takes_context=True)
def hero_item(context, item):
    self = context.get('self')  # Should be onstance of home page.
    return {
        'blog_index': item.link.specific,
        'hero_item': item,
        'request': context['request'],
    }


# Blog hero area, to display the blog index image and title
@register.inclusion_tag('home/tags/blog_hero_item.html', takes_context=True)
def blog_hero_item(context):
    self = context.get('self')
    if self.content_type.model == 'blogindexpage':
        blog_index = self
    else:
        blog_index = self.get_parent().specific
    return {
        'blog_index': blog_index,
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/blog_page_media_item.html', takes_context=True)
def blog_page_media_item(context):
    self = context.get('self')
    media_item = BlogPageMediaItem.objects.get(page=self)
    return {
        'media_item': media_item,
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/blog_index_media_item.html', takes_context=True)
def blog_index_media_item(context, blog):
    self = context.get('self')
    try:
        media_item = BlogPageMediaItem.objects.get(page=blog)
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


@register.inclusion_tag('home/tags/pagination.html', takes_context=True)
def pagination(context):
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


# Social Snippet
@register.inclusion_tag('home/tags/base/social.html', takes_context=True)
def social(context):
    return {
        'socials': Social.objects.select_related('page'),
        'request': context['request'],
    }


# Copyright Snippet
@register.inclusion_tag('home/tags/base/copyright.html', takes_context=True)
def copyright(context):
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
