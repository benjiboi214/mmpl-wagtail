from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, \
    CreateView, UpdateView
from django.core import serializers

from members.models import Player, Venue, Committee

# Create your views here.


class ActionMixin(object):

    @property
    def success_msg(self):
        return NotImplemented

    def form_valid(self, form):
        messages.info(self.request, self.success_msg)
        return super(ActionMixin, self).form_valid(form)


class PlayerActionMixin(ActionMixin):
    fields = [
        'firstname',
        'lastname',
        'dob',
        'email',
        'phone',
        'address',
        'umpire_accreditation',
        'joined',
        'media_release',
        'media_release_date',
        'vanda_policy',
        'vanda_policy_date'
    ]


class PlayerCreateView(LoginRequiredMixin, PlayerActionMixin, CreateView):
    model = Player
    success_msg = 'Player created!'


class PlayerListView(LoginRequiredMixin, ListView):
    model = Player
    template = "members/player_list.html"


class PlayerDetailView(LoginRequiredMixin, DetailView):
    model = Player
    template = "members/player_detail.html"


# class PlayerUpdateView(LoginRequiredMixin, PlayerActionMixin, UpdateView):
#     model = Player
#     success_msg = 'Player updated!'
#     template = "members/player_update.html"


class VenueActionMixin(ActionMixin):
    fields = [
        'name',
        'address',
        'tables',
        'phone',
        'email',
        'contact_name'
    ]


class VenueCreateView(LoginRequiredMixin, VenueActionMixin, CreateView):
    model = Venue
    success_msg = 'Venue created!'


class VenueListView(LoginRequiredMixin, ListView):
    model = Venue
    template = "members/venue_list.html"


class VenueDetailView(LoginRequiredMixin, DetailView):
    model = Venue
    template = "members/venue_detail.html"


class CommitteeActionMixin(ActionMixin):
    fields = [
        'president',
        'vice_president',
        'treasurer',
        'statistician',
        'secretary',
        'assistant_secretary',
        'start_date',
        'end_date'
    ]


class CommitteeCreateView(LoginRequiredMixin, CommitteeActionMixin, CreateView):
    model = Committee
    success_msg = 'Committee created!'


class CommitteeListView(LoginRequiredMixin, ListView):
    model = Committee
    template = "members/committee_list.html"


class CommitteeDetailView(LoginRequiredMixin, DetailView):
    model = Committee
    template = "members/committee_detail.html"


class MemberTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'members/base.html'
