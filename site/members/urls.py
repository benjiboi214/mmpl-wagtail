from django.conf.urls import url
from members.views import PlayerList, PlayerDetail, VenueList, VenueDetail, \
    CommitteeList, CommitteeDetail, MemberHome

urlpatterns = [
    url(r'^players/(?P<slug>[\w\-]+)/$', PlayerDetail.as_view(), name='player_detail'),
    url(r'^players/$', PlayerList.as_view(), name='player_list'),
    # results view (for search for filtering)
    # update view for editing
    url(r'^venues/(?P<slug>[\w\-]+)/$', VenueDetail.as_view(), name='venue_detail'),
    url(r'^venues/$', VenueList.as_view(), name='venue_list'),
    url(r'^committees/(?P<slug>[\w\-]+)/$', CommitteeDetail.as_view(), name='committee_detail'),
    url(r'^committees/$', CommitteeList.as_view(), name='committee_list'),
    url(r'', MemberHome.as_view(), name='members_home')
]
