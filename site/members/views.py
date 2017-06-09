from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, \
    CreateView, UpdateView, DeleteView
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


class PlayerUpdateView(LoginRequiredMixin, PlayerActionMixin, UpdateView):
    model = Player
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


class VenueUpdateView(LoginRequiredMixin, VenueActionMixin, UpdateView):
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


class CommitteeUpdateView(LoginRequiredMixin, CommitteeActionMixin, UpdateView):
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
