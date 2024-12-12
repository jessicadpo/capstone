"""Module for registering models (i.e., SQLite3 database tables)"""

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Item)
admin.site.register(Tag)
admin.site.register(Reward)
admin.site.register(UserProfile)
admin.site.register(UserContribution)

class ReportAdmin(admin.ModelAdmin):
    '''
    Admin view for reporting.
    Creates display fields, filters, and then search fields for navigation.
    '''
    list_display = ('report_id', 'item_id', 'user_id', 'tag', 'reason', 'creation_datetime', 'decision')
    list_filter = ('tag', 'creation_datetime', 'decision', 'user_id')
    search_fields = ('reason', 'user_id__username', 'tag__tag')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

admin.site.register(Report, ReportAdmin)