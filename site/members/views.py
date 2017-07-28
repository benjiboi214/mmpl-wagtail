from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, \
    CreateView, UpdateView, DeleteView
from django.core import serializers
from django.db.models import ProtectedError
from django.http import HttpResponse, HttpResponseRedirect

from members.models import Player, Venue, Committee
from members.forms import PlayerForm, VenueForm, CommitteeForm, \
    CommitteeMemberFormSet


class FormsetMixin(object):
    object = None

    def get(self, request, *args, **kwargs):
        if getattr(self, 'is_update_view', False):
            self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        if getattr(self, 'is_update_view', False):
            self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_formset_class(self):
        return self.formset_class

    def get_formset(self, formset_class):
        return formset_class(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        kwargs = {
            'instance': self.object
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def form_valid(self, form, formset):
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


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
    template_name = "members/venue_list.html"


class VenueDetailView(LoginRequiredMixin, DetailView):
    model = Venue
    template_name = "members/venue_detail.html"


class CommitteeCreateView(LoginRequiredMixin, FormsetMixin, ActionMixin, CreateView):
    template_name = "members/test.html"
    is_update_view = False
    model = Committee
    form_class = CommitteeForm
    formset_class = CommitteeMemberFormSet

#class CommitteeCreateView(LoginRequiredMixin, ActionMixin, CreateView):
#    model = Committee
#    form_class = CommitteeForm
#    success_msg = 'Committee created!'
#    template_name = "members/test.html"
#
#    def form_valid(self, form):
#        context = self.get_context_data()
#        committeemember_form = context['committeemember_form']
#        if committeemember_form.is_valid():
#            self.object = form.save()
#            committeemember_form.instance = self.object
#            committeemember_form.save()
#            return HttpResponseRedirect(self.get_absolute_url())
#        else:
#            return self.render_to_response(self.get_context_data(form=form))
#
#    def form_invalid(self, form):
#        return self.render_to_response(self.get_context_data(form=form))
#
#    def get_context_data(self, **kwargs):
#        context = super(CommitteeCreateView, self).get_context_data(**kwargs)
#        if self.request.POST:
#            context['committeemember_form'] = CommitteeMemberFormSet(self.request.POST)
#        else:
#            context['committeemember_form'] = CommitteeMemberFormSet(instance=self.object)
#        return context
#
#    # TODO:
#    # Get jQuery working for the add and remove buttons
#    # Make sure the update function adds the required existing data
#    # Pull naming up the chain to the Committee object if possible.
#    # Make sure removal of the Comittee via the form removes
#    #   committee member objects and nothing else.
#    # Revisit the validation on the DeleteMixin
#    # Style the formset.

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
