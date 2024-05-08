from django.urls import path
from .views import EventView,EventDetailView,TicketTypeView,TicketView,FeedBackView,EventTeamView,DonarView,SilentAuctionView,HighestBidView, UserRoleView,WishlistView, MessageView,IsPartOfEventView,PendingRSVPView,UserTicketView,EventSearchView,EventImagesView,RandomRaffleView

urlpatterns = [
    path('events/', EventView.as_view(), name='event'),
    path('<int:event_id>/images/',EventImagesView.as_view(),name='images'),
    path('partevent/',IsPartOfEventView.as_view(),name='partof-event'),
    path('events/<int:event_id>/',EventDetailView.as_view(),name='event-details'),
    path('searchevent/',EventSearchView.as_view(),name='search-event'),
    path('<int:event_id>/team/',EventTeamView.as_view(),name='team-details'),
    path('<int:event_id>/ticket/',TicketView.as_view(),name='ticket'),
    path('<int:event_id>/ticket-type/', TicketTypeView.as_view(),name='ticket-type'),
    path('user-ticket/', UserTicketView.as_view(),name='user-ticket'),
    path('<int:event_id>/get-user-role/',UserRoleView.as_view(),name='userrole'),
    path('<int:event_id>/feedback/',FeedBackView.as_view(),name='feedback'),
    path('<int:event_id>/messages/',MessageView.as_view(),name='message'),
    path('user/pending-rsvps/',PendingRSVPView.as_view(),name='invite-request'),
    path('wishlist/', WishlistView.as_view(),name='wishlist'),
    path('<int:event_id>/wishlist/',WishlistView.as_view(),name='remove-wishlist'),
    path('donar/',DonarView.as_view(),name='list-donar'),
    path('<int:event_id>/bid/',SilentAuctionView.as_view(),name='bid-item'),
    path('<int:event_id>/highestbid/', HighestBidView.as_view(),name='high-bid'),
    path('<int:event_id>/raffle/',RandomRaffleView.as_view(),name='raffle-user')
]
