from django import template

from home.models import Social, Copyright, AboutFooter

register = template.Library()


# Social Snippet
@register.inclusion_tag('home/tags/base/social.html', takes_context=True)
def social(context):
    return {
        'socials': Social.objects.select_related('page'),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/base/copyright.html', takes_context=True)
def copyright(context):
    return {
        'copyright': Copyright.objects.select_related('page'),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/base/footer_about.html', takes_context=True)
def aboutfooter(context):
    return {
        'footer': AboutFooter.objects.select_related('page'),
        'request': context['request'],
    }
