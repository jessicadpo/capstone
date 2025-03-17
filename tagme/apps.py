"""Configuration file for Django app"""
import threading
from django.apps import AppConfig
from django.db import connection


class TagMeConfig(AppConfig):
    """Class for implementing app configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tagme'

    def ready(self):
        from tagme.constants import GLOBAL_BLACKLIST, REWARD_LIST  # pylint: disable=import-outside-toplevel
        from tagme.models import Tag, Reward  # pylint: disable=import-outside-toplevel

        def auto_populate_database():
            """Automatically set global blacklist & rewards if database already exists (i.e., already migrated)"""
            if "tagme_tag" in connection.introspection.table_names():
                for word in GLOBAL_BLACKLIST:
                    Tag.objects.get_or_create(tag=word, global_blacklist=True)  # pylint: disable=no-member

            if "tagme_reward" in connection.introspection.table_names():
                points_required = 10
                for title in REWARD_LIST:
                    Reward.objects.get_or_create(title=title, hex_colour=REWARD_LIST.get(title), points_required=points_required)  # pylint: disable=no-member
                    points_required += 60

        threading.Timer(2.0, auto_populate_database).start()  # Execute 2 seconds after ready()
