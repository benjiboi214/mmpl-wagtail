from django.shortcuts import render
from django.views.generic import ListView
from members.models import Player, Venue, Committee

# Create your views here.


class PlayerList(ListView):
    model = Player


class VenueList(ListView):
    model = Venue


class CommitteeList(ListView):
    model = Committee
