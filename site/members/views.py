from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, \
    CreateView, UpdateView, DeleteView
from django.core import serializers

from members.models import Player, Venue, Committee
from members.forms import PlayerForm, VenueForm, CommitteeForm

# Create your views here.


class ActionMixin(object):

    @property
    def success_msg(self):
        return NotImplemented

    def form_valid(self, form):
        messages.info(self.request, self.success_msg)
        return super(ActionMixin, self).form_valid(form)


class PlayerCreateView(LoginRequiredMixin, ActionMixin, CreateView):
    model = Player
    form_class = PlayerForm
    success_msg = 'Player created!'


class PlayerUpdateView(LoginRequiredMixin, ActionMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    success_msg = 'Player updated'


class PlayerDeleteView(LoginRequiredMixin, DeleteView):
    model = Player
    success_url = reverse_lazy('members:player_list')


class PlayerListView(LoginRequiredMixin, ListView):
    model = Player
    template = "members/player_list.html"
    # Add Pagination


class PlayerDetailView(LoginRequiredMixin, DetailView):
    model = Player
    template = "members/player_detail.html"


class VenueCreateView(LoginRequiredMixin, ActionMixin, CreateView):
    model = Venue
    form_class = VenueForm
    success_msg = 'Venue created!'


class VenueUpdateView(LoginRequiredMixin, ActionMixin, UpdateView):
    model = Venue
    success_msg = 'Venue updated'


class VenueDeleteView(LoginRequiredMixin, DeleteView):
    model = Venue
    success_url = reverse_lazy('members:venue_list')


class VenueListView(LoginRequiredMixin, ListView):
    model = Venue
    template = "members/venue_list.html"


class VenueDetailView(LoginRequiredMixin, DetailView):
    model = Venue
    template = "members/venue_detail.html"


class CommitteeCreateView(LoginRequiredMixin, ActionMixin, CreateView):
    model = Committee
    form_class = CommitteeForm
    success_msg = 'Committee created!'


class CommitteeUpdateView(LoginRequiredMixin, ActionMixin, UpdateView):
    model = Committee
    success_msg = 'Committee updated'


class CommitteeDeleteView(LoginRequiredMixin, DeleteView):
    model = Committee
    success_url = reverse_lazy('members:committee_list')


class CommitteeListView(LoginRequiredMixin, ListView):
    model = Committee
    template = "members/committee_list.html"


class CommitteeDetailView(LoginRequiredMixin, DetailView):
    model = Committee
    template = "members/committee_detail.html"


class MemberTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'members/base.html'
