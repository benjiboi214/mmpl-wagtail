from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

from itertools import chain
from operator import attrgetter

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel, StreamFieldPanel, FieldRowPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from wagtail.wagtailforms.forms import FormBuilder

from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, \
    FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock

from modelcluster.fields import ParentalKey
from wagtailmenus.models import MenuPage


# Maybe TODO: Implement tagging. Not sure for what reason, might just be a nice way to filter for relevant information
# TODO: Map the heirachy of the entire site to lock down unnecessary page options when creating.
# TODO: Double check everything in the remaining pages are still legal and reproducible.
# TODO: Clean up home page garbage.
# TODO: Deploy to staging
## Start with new Dataset.
## Scrub Migrations
## Remove unnecessary static objects
# TODO: Revisit email notifications for news object posts.


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
    table = TableBlock(template='home/includes/table.html')


# Link Fields Abstracts
class LinkFieldDocument(models.Model):
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        return self.link_document

    panels = [
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class LinkFieldImage(models.Model):
    link_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        return self.link_image

    panels = [
        ImageChooserPanel('link_image'),
    ]

    class Meta:
        abstract = True


class LinkFieldPage(models.Model):
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        return self.link_page

    panels = [
        PageChooserPanel('link_page'),
    ]

    class Meta:
        abstract = True


class LinkFieldUrl(models.Model):
    link_external = models.URLField("External link", blank=True)

    @property
    def link(self):
        return self.link_external

    panels = [
        FieldPanel('link_external'),
    ]

    class Meta:
        abstract = True


# Link Abstract to pull individual links together above.
class LinkFields(LinkFieldUrl, LinkFieldPage, LinkFieldDocument, LinkFieldImage):
    link_text = models.CharField(max_length=40, blank=True)

    @property
    def link(self):
        if self.link_page:
            return self.link_page
        elif self.link_document:
            return self.link_document
        elif self.link_image:
            return self.link_image
        else:
            return self.link_external

    panels = [
        FieldPanel('link_text'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        ImageChooserPanel('link_image')
    ]

    class Meta:
        abstract = True


# Link Abstract for images and docs
class LinkFieldsDocsImage(LinkFieldDocument, LinkFieldImage):
    link_text = models.CharField(max_length=40, blank=True)

    @property
    def link(self):
        if self.link_document:
            return self.link_document
        else:
            return self.link_image

    panels = [
        FieldPanel('link_text'),
        DocumentChooserPanel('link_document'),
        ImageChooserPanel('link_image')
    ]

    class Meta:
        abstract = True


# Link Abstract for images and external links
class LinkFieldsUrlImage(LinkFieldUrl, LinkFieldImage):
    link_text = models.CharField(max_length=40, blank=True)

    @property
    def link(self):
        if self.link_external:
            return self.link_external
        else:
            return self.link_image

    panels = [
        FieldPanel('link_text'),
        FieldPanel('link_external'),
        ImageChooserPanel('link_image')
    ]

    class Meta:
        abstract = True


class BlogPageMediaItem(LinkFieldsUrlImage):
    page = ParentalKey('home.BlogPage', related_name='media_item')


class BlogPage(Page):
    body = StreamField(HomeStreamBlock())
    date = models.DateField("Post date")

    parent_page_types = [
        'home.SeasonPage',
        'home.BlogIndexPage',
        'home.AboutPage'
    ]

    @property
    def intro(self):
        intro = []
        for block in self.body:
            if block.block_type == 'intro':
                intro.append(block)
        return intro

    class Meta:
        verbose_name = "Blog Page"

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


class BlogIndexPage(MenuPage):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    subpage_types = [
        'home.BlogIndexPage',
        'home.BlogPage',
        'home.DocumentPage'
    ]
    parent_page_types = [
        'home.SeasonPage',
        'home.BlogIndexPage',
    ]

    @property
    def blogs(self):
        blogs = BlogPage.objects.live().child_of(self)
        blogs = blogs.order_by('-date')
        return blogs

    @property
    def documents(self):
        documents = DocumentPage.objects.live().child_of(self)
        documents = documents.order_by('-date')
        return documents

    def get_context(self, request):
        results = sorted(
            chain(self.blogs, self.documents),
            key=attrgetter('date')
        )

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(results, 10)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        context = super(BlogIndexPage, self).get_context(request)
        context['paginator'] = blogs
        return context

    class Meta:
        verbose_name = "Blog Index Page"

    content_panels = [
        FieldPanel('title', classname='full title'),
        ImageChooserPanel('image'),
    ]


class AboutPageContactItem(LinkFieldPage, Orderable):
    page = ParentalKey('home.AboutPage', related_name='contact_item')
    intro = models.CharField(max_length=300, blank=True)
    icon = models.CharField(max_length=20, verbose_name="Icon Code (fa)")

    panels = [
        FieldPanel('intro'),
        FieldPanel('icon'),
        PageChooserPanel('link_page'),
    ]


class AboutPage(MenuPage):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    sub_title = models.CharField(max_length=50, blank=True)
    body = RichTextField(blank=True)
    join_item_title = models.CharField(max_length=25, blank=True)

    subpage_types = [
        'home.AboutPage',
        'home.BlogPage',
        'home.ContactFormPage'
    ]
    parent_page_types = [
        'home.SeasonPage',
        'home.AboutPage'
    ]

    @property
    def contact_items(self):
        contact_items = AboutPageContactItem.objects.filter(page=self)
        return contact_items

    def get_context(self, request):
        contact_items = self.contact_items
        pages = len(contact_items)
        if pages % 3 == 0:
            col = 4
        elif pages % 2 == 0:
            col = 6
        elif pages % 1 == 0:
            col = 6
        context = super(AboutPage, self).get_context(request)
        context['contact_items'] = contact_items
        context['contact_items_col'] = col
        return context

    class Meta:
        verbose_name = "About Page"

AboutPage.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('image'),
    FieldPanel('sub_title'),
    FieldPanel('body', classname="full"),
    MultiFieldPanel(
        [
            FieldPanel('join_item_title'),
            InlinePanel(
                'contact_item',
                label="Contact Form Item",
            ),
        ]
    )
]


# Abstract for adding CSS and Placeholder attrs to widget
class CustomFormBuilder(FormBuilder):
    @property
    def formfields(self):
        formfields = OrderedDict()

        for field in self.fields:
            options = self.get_field_options(field)

            if field.field_type in self.FIELD_TYPES:
                # import pdb; pdb.set_trace()
                formfields[field.clean_name] = self.FIELD_TYPES[field.field_type](self, field, options)
            else:
                raise Exception("Unrecognised field type: " + field.field_type)
            if hasattr(formfields[field.clean_name], 'widget'):
                widget = formfields[field.clean_name].widget
                large_widgets = ['multiline', 'radio', 'checkboxes']
                if field.field_type in large_widgets:
                    widget.large = True
                else:
                    widget.large = False
                cls_attrs = 'form-control input-lg'
                widget.attrs['class'] = cls_attrs
                widget.attrs['placeholder'] = field.label
        return formfields


class ContactFormField(AbstractFormField):
    page = ParentalKey('ContactFormPage', related_name='form_fields')


class ContactFormPage(AbstractEmailForm):
    sub_title = models.CharField(max_length=50, blank=True)
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    form_builder = CustomFormBuilder

    parent_page_types = ['home.AboutPage']

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('sub_title', classname="full"),
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
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


class Competition(models.Model):
    page = ParentalKey('home.SeasonPage', related_name='competitions')
    title = models.CharField(
        max_length=50,
        verbose_name="Division Name (Tab Display)"
    )
    poolstat_url = models.CharField(
        max_length=255,
        verbose_name="Poolstat Competition URL (Ladder Link)")


    panels = [
        FieldPanel('title'),
        FieldPanel('poolstat_url')
    ]


class SeasonPage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subpage_types = [
        'home.VenueIndexPage',
        'home.BlogIndexPage',
        'home.BlogPage',
        'home.DocumentPage',
        'home.AboutPage'
    ]
    parent_page_types = ['wagtailcore.Page']

    def news_index(self):
        return BlogIndexPage.objects.live().child_of(self).first()

    @property
    def primary_news(self):
        return BlogPage.objects.live().child_of(self.news_index()).order_by('latest_revision_created_at').first()

    class Meta:
        verbose_name = "Season Page"


SeasonPage.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('image'),
    InlinePanel(
        'news_item',
        label='News',
        max_num=1
    ),
    InlinePanel(
        'competitions',
        label="Competitions"
    ),
]


class VenuePage(Page):
    '''Venue Page object for adding and displaying venues as a part
    of the new season centric layout of the website.'''
    blurb = models.CharField(max_length=500, blank=True)

    @property
    def photos(self):
        return self.venue_details.photos.all().order_by('-photo')

    @property
    def photo(self):
        return self.venue_details.photos.all().order_by('photo')[0]

    @property
    def open_hours(self):
        return self.venue_details.openhours.all().order_by('open_day')

    class Meta:
        verbose_name = "Venue Page"
    
    parent_page_types = ['home.VenueIndexPage']


VenuePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('blurb'),
]


class VenueIndexPage(Page):
    subpage_types = [
        'home.VenuePage',
    ]
    parent_page_types = ['home.SeasonPage']

    @property
    def venues(self):
        venues = VenuePage.objects.live().child_of(self)

        venues = venues.order_by('title')
        return venues

    def get_context(self, request):
        venues = self.venues

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(venues, 20)
        try:
            venues = paginator.page(page)
        except PageNotAnInteger:
            venues = paginator.page(1)
        except EmptyPage:
            venues = paginator.page(paginator.num_pages)

        context = super(VenueIndexPage, self).get_context(request)
        context['paginator'] = venues
        return context

    class Meta:
        verbose_name = "Venue Index Page"


VenueIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
]


class MediaItem(LinkFieldsDocsImage):
    page = ParentalKey('home.DocumentPage', related_name='media_item')


class NewsItem(LinkFieldPage):
    page = ParentalKey('home.SeasonPage', related_name='news_item')

    def _check_page_type(self):
        if self.link_page.content_type.model == 'blogindexpage':
            return True
        else:
            return False

    def primary(self):
        if self._check_page_type():
            return BlogPage.objects.live().child_of(self.link_page).order_by('-date')[0:1]

    def secondary(self):
        if self._check_page_type():
            return BlogPage.objects.live().child_of(self.link_page).order_by('-date')[1:4] 
    # if doc page type is blogpageindex
    # get primary news item
    # get three secondary news items


class DocumentPage(Page):
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Description"
    )
    date = models.DateField("Post date")

    subpage_types = []
    parent_page_types = [
        'home.SeasonPage',
        'home.BlogIndexPage'
    ]

    class Meta:
        verbose_name = "Document Page"

DocumentPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    FieldPanel('description', classname='full'),
    InlinePanel('media_item', label="Document / Image")
]
