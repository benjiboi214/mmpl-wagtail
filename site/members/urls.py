from django.conf.urls import url
from members.views import PlayerList, PlayerDetail, VenueList, VenueDetail, \
    CommitteeList, CommitteeDetail

urlpatterns = [
    url(r'^players/(?P<slug>[\w\-]+)/$', PlayerDetail.as_view(), name='player_detail'),
    url(r'^players/$', PlayerList.as_view(), name='player_list'),
    url(r'^venues/(?P<slug>[\w\-]+)/$', VenueDetail.as_view(), name='venue_detail'),
    url(r'^venues/$', VenueList.as_view(), name='venue_list'),
    url(r'^committee/(?P<slug>[\w\-]+)/$', CommitteeDetail.as_view(), name='committee_detail'),
    url(r'^committee/$', CommitteeList.as_view(), name='committee_list'),
]
