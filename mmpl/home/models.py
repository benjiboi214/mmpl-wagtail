from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey


# Link Abstract
class LinkFields(models.Model):
    link_text = models.CharField(max_length=40, blank=True)
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page
        elif self.link_document:
            return self.link_document
        else:
            return self.link_external

    panels = [
        FieldPanel('link_text'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


# Carousel Abstract
class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    title = models.CharField(max_length=25)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('title'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class HeroItem(LinkFields):
    title = models.CharField(max_length=25, blank=True)
    page = ParentalKey('home.HomePage', related_name='hero_items')
    blurb = models.CharField("Blurb", max_length=255, blank=True)

    panels = [
        FieldPanel('title', classname='full'),
        FieldPanel('blurb'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]


# Home Page Classes
class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('home.HomePage', related_name='carousel_items')


class HomePage(Page):
    hero_item_title = models.CharField(max_length=25, blank=True)
    hero_item_blurb = RichTextField(blank=True)

    class Meta:
        verbose_name = "Homepage"


HomePage.content_panels = [
    FieldPanel('title', classname='full title'),
    InlinePanel('carousel_items', label="Carousel items"),
    MultiFieldPanel(
        [
            FieldPanel('hero_item_title'),
            FieldPanel('hero_item_blurb'),
            InlinePanel(
                'hero_items',
                label="Hero Items",
                max_num=3
            ),
        ],
        heading="Home Page Hero Items",
        classname="collapsible"
    ),
]


class BlogIndexPage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        FieldPanel('title', classname='full title'),
        ImageChooserPanel('image'),
    ]


class BlogPage(Page):
    panels = [
        FieldPanel('title', classname='full title')
    ]


# Social Snippet
@register_snippet
class Social(LinkFields):
    title = models.CharField(max_length=50, verbose_name="Social Site")
    page = models.ForeignKey(
        'wagtailcore.Page',
        related_name='social',
        null=True,
        blank=True
    )
    icon = models.CharField(max_length=20, verbose_name="Icon Code (fa)")

    panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('link_external'),
        FieldPanel('icon')
    ]

    def __unicode__(self):
        return self.title


# Copyight Snippet
@register_snippet
class Copyright(models.Model):
    copyright = models.CharField(
        max_length=100,
        verbose_name="Copyright Footer"
    )
    page = models.ForeignKey(
        'wagtailcore.Page',
        related_name='copyright',
        null=True,
        blank=True
    )

    panels = [
        FieldPanel('copyright', classname='full title')
    ]

    def __unicode__(self):
        return self.copyright


# Footer Snippet
@register_snippet
class AboutFooter(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name="Header"
    )
    body = models.CharField(
        max_length=500,
        verbose_name="Body"
    )
    page = models.ForeignKey(
        'wagtailcore.Page',
        related_name='footer_about',
        null=True,
        blank=True
    )

    panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('body')
    ]

    def __unicode__(self):
        return self.title


# Logo Snippet
@register_snippet
class Logo(models.Model):
    description = models.CharField(
        max_length=100,
        verbose_name="Description"
    )
    page = models.ForeignKey(
        'wagtailcore.Page',
        related_name='logo',
        null=True,
        blank=True
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='image'
    )

    panels = [
        FieldPanel('description', classname='full title'),
        ImageChooserPanel('image')
    ]

    def __unicode__(self):
        return self.description
