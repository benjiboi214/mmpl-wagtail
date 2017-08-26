from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

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
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
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


# Home Page Classes
class HeroItem(LinkFields):
    title = models.CharField(max_length=25, blank=True)
    page = ParentalKey('home.HomePage', related_name='hero_items')
    blurb = models.CharField("Blurb", max_length=255, blank=True)

    panels = [
        FieldPanel('title', classname='full'),
        FieldPanel('blurb'),
        MultiFieldPanel(
            [FieldPanel('link_text'),
             PageChooserPanel('link_page'),
             ],
            "Link"
        ),
    ]


class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('home.HomePage', related_name='carousel_items')


class HomePage(MenuPage):
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

    @property
    def blogs(self):
        # Get list of live blog pages that are descendants of this page

        # Selects all descendants of index page, to diaplay on index.
        # blogs = BlogPage.objects.live().descendant_of(self)
        # Selects direct descendants of index page.
        blogs = BlogPage.objects.live().child_of(self)

        # Order by most recent date first
        blogs = blogs.order_by('-date')
        return blogs

    def get_context(self, request):
        # Get blogs
        blogs = self.blogs

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(blogs, 10)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['paginator'] = blogs
        return context

    class Meta:
        verbose_name = "Blog Index Page"

    content_panels = [
        FieldPanel('title', classname='full title'),
        ImageChooserPanel('image'),
    ]


class AboutPageContactItem(LinkFields, Orderable):
    page = ParentalKey('home.AboutPage', related_name='contact_item')
    intro = models.CharField(max_length=300, blank=True)
    icon = models.CharField(max_length=20, verbose_name="Icon Code (fa)")

    panels = [
        FieldPanel('intro'),
        FieldPanel('icon'),
        PageChooserPanel('link_page'),
    ]


class SeasonPage(Page):

    class Meta:
        verbose_name = "Season Page"


SeasonPage.content_panels = [
    FieldPanel('title', classname='full title'),
]


class VenuePage(Page):
    '''Venue Page object for adding and displaying venues as a part
    of the new season centric layout of the website.'''
    # TODO Link Venue Page as a child of Venue Index
    # TODO Add help text to admin page to make it obvious what is happening

    blurb = models.CharField(max_length=500, blank=True)

    @property
    def photos(self):
        return self.venue_details.photos.all().order_by('-photo')

    @property
    def open_hours(self):
        return self.venue_details.openhours.all().order_by('open_day')

    class Meta:
        verbose_name = "Venue Page"


VenuePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('blurb'),
]


class VenueIndexPage(Page):

    class Meta:
        verbose_name = "Venue Index Page"


VenueIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
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
