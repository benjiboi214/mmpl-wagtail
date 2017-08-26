# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-26 07:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0033_remove_golive_expiry_help_text'),
        ('home', '0008_auto_20170410_0541'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeasonPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'verbose_name': 'Season Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='VenueIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'verbose_name': 'Venue Index Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='VenuePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('blurb', models.CharField(blank=True, max_length=500)),
            ],
            options={
                'verbose_name': 'Venue Page',
            },
            bases=('wagtailcore.page',),
        ),
    ]
