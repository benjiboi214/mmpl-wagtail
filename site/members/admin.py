from django.contrib import admin
from .models import Player, Notification, Venue, Committee


class NotificationInline(admin.StackedInline):
    model = Notification
    extra = 0


class PlayerAdmin(admin.ModelAdmin):
    inlines = [
        NotificationInline
    ]
    list_display = ('firstname', 'lastname', 'email', 'phone')
    search_fields = ['firstname', 'lastname']
    readonly_fields = ['updated']


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'tables', 'contact_name')
    search_fields = ['name']

class CommitteeAdmin(admin.ModelAdmin):
    list_display =  ('start_date', 'end_date')

admin.site.register(Player, PlayerAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Committee, CommitteeAdmin)
