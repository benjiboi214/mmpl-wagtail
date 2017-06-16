from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, \
    CreateView, UpdateView, DeleteView
from django.core import serializers
from django.db.models import ProtectedError
from django.http import HttpResponse, HttpResponseRedirect

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


class DeleteMixin(object):

    @property
    def success_msg(self):
        return NotImplemented

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.info(request, self.success_msg)
            return HttpResponseRedirect(success_url)
        except ProtectedError, e:
            msg = 'Cannot delete %s. Object is a member of protected objects:'
            for p in e.protected_objects:
                msg += '<br>'
                p_msg = "%s: %s" % (p._meta.object_name, p)
                msg += p_msg
            messages.error(request, (msg % self.object), extra_tags='safe')
            return HttpResponseRedirect(self.object.get_absolute_url())


class PlayerCreateView(LoginRequiredMixin, ActionMixin, CreateView):
    model = Player
    form_class = PlayerForm
    success_msg = 'Player created!'


class PlayerUpdateView(LoginRequiredMixin, ActionMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    success_msg = 'Player updated.'


class PlayerDeleteView(LoginRequiredMixin, ActionMixin, DeleteMixin, DeleteView):
    # Check for preexisting foreign key relations before deleting
    model = Player
    success_url = reverse_lazy('members:player_list')
    success_msg = 'Player removed.'


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
    success_msg = 'Venue updated.'


class VenueDeleteView(LoginRequiredMixin, ActionMixin, DeleteMixin, DeleteView):
    model = Venue
    success_url = reverse_lazy('members:venue_list')
    success_msg = 'Venue removed.'


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
    success_msg = 'Committee updated.'


class CommitteeDeleteView(LoginRequiredMixin, ActionMixin, DeleteMixin, DeleteView):
    model = Committee
    success_msg = 'Committee removed.'
    success_url = reverse_lazy('members:committee_list')


class CommitteeListView(LoginRequiredMixin, ListView):
    model = Committee
    template = "members/committee_list.html"


class CommitteeDetailView(LoginRequiredMixin, DetailView):
    model = Committee
    template = "members/committee_detail.html"


class MemberTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'members/base.html'
