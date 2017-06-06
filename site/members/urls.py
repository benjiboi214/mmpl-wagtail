from django.conf.urls import url
from members.views import PlayerListView, PlayerDetailView, PlayerCreateView, \
    PlayerUpdateView, PlayerDeleteView, VenueListView, VenueDetailView, \
    VenueCreateView, VenueUpdateView, VenueDeleteView, CommitteeListView, \
    CommitteeDetailView, CommitteeCreateView, CommitteeUpdateView, \
    CommitteeDeleteView, MemberTemplateView

app_name = 'members'
urlpatterns = [
    url(r'^players/(?P<slug>[\w\-]+)/$',
        PlayerDetailView.as_view(),
        name='player_detail'),
    url(r'^players/(?P<slug>[\w\-]+)/update$',
        PlayerUpdateView.as_view(),
        name='player_update'),
    url(r'^players/(?P<slug>[\w\-]+)/delete$',
        PlayerDeleteView.as_view(),
        name='player_delete'),
    url(r'^players/add$', PlayerCreateView.as_view(), name='player_add'),
    url(r'^players/$', PlayerListView.as_view(), name='player_list'),
    # results view (for search for filtering)
    # update view for editing
    url(r'^venues/(?P<slug>[\w\-]+)/$',
        VenueDetailView.as_view(),
        name='venue_detail'),
    url(r'^venues/(?P<slug>[\w\-]+)/update$',
        VenueUpdateView.as_view(),
        name='venue_update'),
    url(r'^venues/(?P<slug>[\w\-]+)/delete$',
        VenueDeleteView.as_view(),
        name='venue_delete'),
    url(r'^venues/add$', VenueCreateView.as_view(), name='venue_add'),
    url(r'^venues/$', VenueListView.as_view(), name='venue_list'),
    url(r'^committees/(?P<slug>[\w\-]+)/$',
        CommitteeDetailView.as_view(),
        name='committee_detail'),
    url(r'^committees/(?P<slug>[\w\-]+)/update$',
        CommitteeUpdateView.as_view(),
        name='committee_update'),
    url(r'^committees/(?P<slug>[\w\-]+)/delete$',
        CommitteeDeleteView.as_view(),
        name='committee_delete'),
    url(r'^committees/add$', CommitteeCreateView.as_view(), name='committee_add'),
    url(r'^committees/$', CommitteeListView.as_view(), name='committee_list'),
    url(r'', MemberTemplateView.as_view(), name='members_base')
]
