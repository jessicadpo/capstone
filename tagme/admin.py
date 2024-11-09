"""Module for registering models (i.e., SQLite3 database tables)"""

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Tag)
