from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.core import serializers

from members.models import Player, Venue, Committee

# Create your views here.


class PlayerList(ListView):
    model = Player


class PlayerDetail(DetailView):
    model = Player


class VenueList(ListView):
    model = Venue


class VenueDetail(DetailView):
    model = Venue


class CommitteeList(ListView):
    model = Committee


class CommitteeDetail(DetailView):
    model = Committee


class MemberHome(TemplateView):
    template_name = 'members/base.html'
