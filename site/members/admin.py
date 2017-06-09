from django.contrib import admin
from .models import Player, Notifications, Venue, Committee


class NotificationsInline(admin.StackedInline):
    model = Notifications
    extra = 0


class PlayerAdmin(admin.ModelAdmin):
    inlines = [
        NotificationsInline
    ]
    list_display = ('firstname', 'lastname', 'email', 'phone')
    search_fields = ['firstname', 'lastname']
    readonly_fields = ['updated']


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'tables', 'contact_name')
    search_fields = ['name']

class CommitteeAdmin(admin.ModelAdmin):
    list_display =  ('president', 'start_date', 'end_date')

admin.site.register(Player, PlayerAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Committee, CommitteeAdmin)