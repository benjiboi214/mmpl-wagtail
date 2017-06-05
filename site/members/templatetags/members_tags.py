from django import template

register = template.Library()


@register.inclusion_tag('home/tags/test_context.html', takes_context=True)
def test_context(context):
    # self = context.get('self')  # Should be onstance of home page.
    import pdb; pdb.set_trace()
    return {
        #'self': self,
        'request': context['request'],
    }


@register.inclusion_tag('members/tags/navigation_sidebar.html', takes_context=True)
def navigation_sidebar(context):
    return {
        'request': context['request'],
    }
