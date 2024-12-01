"""Module for registering models (i.e., SQLite3 database tables)"""

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Item)
admin.site.register(Tag)
admin.site.register(Reward)
admin.site.register(UserProfile)
admin.site.register(UserContribution)
admin.site.register(Report)
