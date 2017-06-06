from __future__ import unicode_literals
from datetime import date

from django.db import models

from address.models import AddressField
from slugify import UniqueSlugify


class Player(models.Model):
    '''Model for recording player related data. To start, covers all
    information included in the player registration form,'''
    ACCREDITATION_CHOICES = (
        ('A', 'A Grade'),
        ('B', 'B Grade'),
        ('C', 'C Grade'),
        ('D', 'D Grade'),
        ('N', 'None'),
    )

    firstname = models.CharField(max_length=64, verbose_name='First Name')
    lastname = models.CharField(max_length=64, verbose_name='Last Name')
    dob = models.DateField(verbose_name='Date of Birth')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(
        max_length=15,
        verbose_name='Phone Number',
        blank=True)
    address = AddressField(
        related_name='player',
        verbose_name='Address')
    umpire_accreditation = models.CharField(
        max_length=1,
        choices=ACCREDITATION_CHOICES,
        default='N',
        verbose_name='Umpire Accreditation')
    joined = models.DateField(default=date.today, verbose_name='Join Date')
    updated = models.DateField(auto_now=True, verbose_name='Last Updated')
    media_release = models.BooleanField(
        default=False,
        verbose_name='Media Release')
    media_release_date = models.DateField(
        verbose_name='Media Release Signed Date',
        blank=True)
    vanda_policy = models.BooleanField(
        default=False,
        verbose_name='Violence and Aggression Policy Agreement')
    vanda_policy_date = models.DateField(
        verbose_name='Violence and Aggression Policy Agreement Date',
        blank=True)
    slug = models.SlugField(blank=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('members:player_detail', args=[self.slug])

    def save(self, **kwargs):
        unique_slugify = UniqueSlugify(to_lower=True)
        self.slug = unique_slugify(self.__unicode__())
        super(Player, self).save(**kwargs)

    def __unicode__(self):
        return "%s %s" % (self.firstname, self.lastname)


class Notifications(models.Model):
    '''Model for tracking notifications preferences for various parts of the
    website.'''
    NOTIFICATION_CHOICES = (
        ('M', 'Mobile'),
        ('E', 'Email')
    )
    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        primary_key=True
    )
    preference = models.CharField(
        max_length=1,
        choices=NOTIFICATION_CHOICES,
        default='E',
        verbose_name='Notification Preference'
    )
    events = models.BooleanField(default=True)
    results = models.BooleanField(default=True)
    resources = models.BooleanField(default=True)
    news = models.BooleanField(default=True)


class Venue(models.Model):
    '''Model for tracking Venues visited by the league. Contains all relevant
    information for contacting venue, as well as housing the number of
    tables available to be used in fixture generation.'''
    name = models.CharField(max_length=128)
    address = AddressField(related_name='venue', verbose_name='Address')
    tables = models.PositiveIntegerField(verbose_name='Number of Tables')
    phone = models.CharField(max_length=15, verbose_name='Phone Number')
    email = models.EmailField(verbose_name='Email')
    contact_name = models.CharField(
        max_length=128,
        blank=True,
        verbose_name='Contact Name')
    # Has hours of operation https://github.com/arteria/django-openinghours
    slug = models.SlugField(blank=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('members:venue_detail', args=[self.slug])

    def save(self, **kwargs):
        unique_slugify = UniqueSlugify(to_lower=True)
        self.slug = unique_slugify(self.__unicode__())
        super(Venue, self).save(**kwargs)

    def __unicode__(self):
        return self.name


class Committee(models.Model):
    '''Model for recording Committee membership. Creating a new entry per year
    for each new committee voted in will serve as a historical record of
    members service, as well as presenting current committee'''
    president = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='president',
        verbose_name='President')
    vice_president = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='vice_president',
        verbose_name='Vice President')
    treasurer = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='treasurer',
        verbose_name='Treasurer')
    statistician = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='statistician',
        verbose_name='Statistician')
    secretary = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='secretary',
        verbose_name='Secretary')
    assistant_secretary = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='assistant_secretary',
        verbose_name='Assistant Secretary')
    start_date = models.DateField(
        default=date.today,
        verbose_name='Election Date')
    end_date = models.DateField(
        default=date.today,
        verbose_name='End Date')
    slug = models.SlugField(blank=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('members:committee_detail', args=[self.slug])

    def save(self, **kwargs):
        unique_slugify = UniqueSlugify(to_lower=True)
        self.slug = unique_slugify(self.__unicode__())
        super(Committee, self).save(**kwargs)

    def __unicode__(self):
        return "%s: %s-%s" % (
            self.president,
            self.start_date.year,
            self.end_date.year
        )
