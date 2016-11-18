from django import template

from home.models import Social, Copyright, AboutFooter, Logo, HeroItem, \
    Page

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
@register.inclusion_tag('home/tags/hero_item.html', takes_context=True)
def hero_item(context, item):
    self = context.get('self')  # Should be onstance of home page.
    return {
        'blog_index': item.link.specific,
        'hero_item': item,
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
    print ancestors
    return {
        'ancestors': ancestors,
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
