"""Module for defining models (i.e., SQLite3 database tables)"""
from django.db import models
from django.contrib.auth.models import User


class UserContributions(models.Model):
    """Class for UserContributions database table"""
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    # TODO: Add rest of attributes (just doing this to pass linter for now)
