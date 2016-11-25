from __future__ import absolute_import, unicode_literals

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, \
    FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from modelcluster.fields import ParentalKey


# Global Streamfield Definitions
class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'),
        ('right', 'Wrap right'),
        ('mid', 'Mid width'),
        ('full', 'Full width'),
    ))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class HomeStreamBlock(StreamBlock):
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")


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


class BlogPageMediaItem(LinkFields):
    page = ParentalKey('home.BlogPage', related_name='media_item')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('link_external')
    ]


class BlogPage(Page):
    body = StreamField(HomeStreamBlock())
    date = models.DateField("Post date")

    @property
    def blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()

    @property
    def intro(self):
        intro = []
        for block in self.body:
            if block.block_type == 'intro':
                intro.append(block)
        return intro

BlogPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    InlinePanel(
        'media_item',
        label="Media Item",
        max_num=1,
        help_text="""
        Always get the URL from the 'src' section of the 'embed' option.
        Used for populating the blog index media items, and blog page media
        items. Will try to populate external links first, then image and
        finally ignore and fill space.
        """
    ),
    StreamFieldPanel('body')
]


class BlogIndexPage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def blogs(self):
        # Get list of live blog pages that are descendants of this page
        blogs = BlogPage.objects.live().descendant_of(self)

        # Order by most recent date first
        blogs = blogs.order_by('-date')
        return blogs

    def get_context(self, request):
        # Get blogs
        blogs = self.blogs

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(blogs, 1)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['blogs'] = blogs
        return context

    content_panels = [
        FieldPanel('title', classname='full title'),
        ImageChooserPanel('image'),
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
