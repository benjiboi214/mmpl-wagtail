from django.conf.urls import url
from members.views import PlayerList, VenueList, CommitteeList

urlpatterns = [
    url(r'^players/$', PlayerList.as_view()),
    url(r'^venues/$', VenueList.as_view()),
    url(r'^committees/$', CommitteeList.as_view()),
]
