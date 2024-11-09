"""Module for registering models (i.e., SQLite3 database tables)"""

from django.contrib import admin
from .models import UserContributions

# Register your models here.
admin.site.register(UserContributions)
