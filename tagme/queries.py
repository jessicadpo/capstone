# pylint: disable=no-member
"""
Module for querying models AND Library of Congress & Datamuse APIs

RATE LIMIT FOR LIBRARY OF CONGRESS API: 20 queries per 10 seconds && 80 queries per 1 minute
"""
from urllib.parse import quote
from django.db import connection
from django.db.models import Count
from django.contrib.auth import PermissionDenied
from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
import requests
from .apps import TagMeConfig
from .helper_functions import *
from .models import *
from .constants import *


########################################################################################################################
# DJANGO DATABASE QUERIES

#######################################################
# GETTERS

def get_is_item_pinned(user, item_id):
    """Function for checking whether the user currently has a given item_id in their pins"""
    user_contrib = UserContribution.objects.filter(user_id=user.id, item_id=item_id)
    if user_contrib.exists():
        return user_contrib[0].is_pinned
    return False


def get_all_tags_for_user(user):
    """Function for getting all tags added by a particular user (on any PINNED item)"""
    print(f'placeholder code {user}')


def get_all_tags_for_item(item_id):
    """Function for getting all tags for a particular item_id"""
    item = Item.objects.filter(item_id=item_id)
    if item.exists():
        # Return an array of dicts, each dict contains a tag and its count
        # Exclude contributions with 0 public tags
        public_tags_with_counts = (UserContribution.objects
                                   .filter(item_id=item_id)
                                   .values('public_tags')
                                   .annotate(count=Count('public_tags'))
                                   .filter(count__gt=0)
                                   .order_by('-count'))

        # Rename "public_tags" key to just "tag"
        for tag_dict in public_tags_with_counts:
            tag_dict['tag'] = tag_dict.pop('public_tags')

        return public_tags_with_counts
    return None


def get_user_tags_for_item(user, item_id):
    """Function for retrieving a user's tags for a particular item"""
    if not user.is_authenticated:
        raise PermissionDenied("User must be logged in")

    # Returns a list of dicts (each tag in its own dict)
    user_contrib = UserContribution.objects.filter(user_id=user.id, item_id=item_id)
    if user_contrib.exists():
        user_contrib = user_contrib[0]
        public_tags = list(user_contrib.public_tags.all().values('tag'))
        private_tags = list(user_contrib.private_tags.all().values('tag'))

        # Reformat array of dicts into array of strings
        user_public_tags = [list(tag.values())[0] for tag in public_tags]
        user_private_tags = [list(tag.values())[0] for tag in private_tags]

        return user_public_tags, user_private_tags
    return None, None


def get_user_points_for_item(user, item_id):
    """Function for retrieving the number of points already earned by user for (public) tagging a particular item"""
    if not user.is_authenticated:
        raise PermissionDenied("User must be logged in")

    # Returns a list of dicts (each tag in its own dict)
    user_contrib = UserContribution.objects.filter(user_id=user.id, item_id=item_id)
    if user_contrib.exists():
        return user_contrib[0].points_earned
    return 0


def get_user_total_points(user):
    """Function for getting a user's current total number of points"""
    user_profile = UserProfile.objects.filter(user=user)
    if user_profile.exists():
        return user_profile[0].points
    return 0


def get_equipped_titles(user):
    """Function for getting a user's currently equipped titles"""
    equipped_title_1 = None
    equipped_title_2 = None

    user_profile = UserProfile.objects.filter(user=user)
    if user_profile.exists():
        equipped_title_1_object = Reward.objects.filter(title=user_profile[0].equipped_title_1)
        equipped_title_2_object = Reward.objects.filter(title=user_profile[0].equipped_title_2)

        if equipped_title_1_object.exists():
            equipped_title_1 = reward_to_dict_format(equipped_title_1_object)

        if equipped_title_2_object.exists():
            equipped_title_2 = reward_to_dict_format(equipped_title_2_object)

    return equipped_title_1, equipped_title_2


def get_earned_rewards(user):
    """Function for getting all rewards already earned by a user"""
    total_points = get_user_total_points(user)
    earned_rewards = Reward.objects.filter(points_required__lte=total_points)
    if earned_rewards.exists():
        # Format as an array to keep consistent with other get_rewards()/get_titles() functions
        earned_rewards_list = []
        for reward in earned_rewards:
            earned_rewards_list.append(reward_to_dict_format(reward))
        return earned_rewards_list
    return None


def get_next_reward(user):
    """Function for getting the next reward the user can earn (i.e., reward is NOT earned yet)"""
    total_points = get_user_total_points(user)
    next_reward = Reward.objects.filter(points_required__gt=total_points).order_by("points_required")
    if next_reward.exists():
        # Format as an array to keep consistent with other get_rewards()/get_titles() functions
        return [reward_to_dict_format(next_reward[0])]
    return None


def get_new_rewards(prev_score, new_score):
    """Function for checking if a user should get a new reward + returning the new reward they should be getting"""
    new_rewards = Reward.objects.filter(points_required__gt=prev_score).filter(points_required__lte=new_score)
    if new_rewards.exists():
        new_rewards_list = []  # Format as an array to keep consistent with other get_rewards()/get_titles() functions
        for reward in new_rewards:
            new_rewards_list.append(reward_to_dict_format(reward))
        return new_rewards_list
    return None


def get_synonymous_tags(search_string):
    """Function for getting tags that are synonyms of a list of given words"""
    # TODO: Parse AND/OR/NOT

    synonyms = query_datamuse_synonyms(search_string)
    synonymous_tags = []
    for synonym in synonyms:
        synonym_tag = Tag.objects.filter(tag=synonym)
        if synonym_tag.exists():
            # Need to format it as a dict to stay consistent with return format of get_all_tags_for_item()
            synonymous_tags.append({"tag": synonym_tag[0].tag})

    # TODO: Need a way to determine which tags more relevant (so can list the most relevant ones first)

    return synonymous_tags


def get_related_tags(search_string):
    """Function for getting tags that are related to a list of given words"""
    # TODO: Parse AND/OR/NOT

    related_words = query_datamuse_related_words(search_string)
    related_tags = []
    for related_word in related_words:
        related_tag = Tag.objects.filter(tag=related_word)
        if related_tag.exists():
            # Need to format it as a dict to stay consistent with return format of get_all_tags_for_item()
            related_tags.append({"tag" : related_tag[0].tag})

    # TODO: Need a way to determine which tags more relevant (so can list the most relevant ones first)

    return related_tags


#######################################################
# SETTERS

def set_user_tags_for_item(user, tags_data):
    """Function for adding/updating a user's tags for a particular item"""
    item_id = tags_data.get('tagged_item')
    public_tags = tags_data.get('public_tags')  # All tags in a single string
    private_tags = tags_data.get('private_tags')

    # Convert tag strings into lists / arrays
    # Use filter to remove any empty elements from tag list
    if len(public_tags) > 0:
        public_tags = list(filter(lambda tag: tag, public_tags.split('\\n')))
    if len(private_tags) > 0:
        private_tags = list(filter(lambda tag: tag, private_tags.split('\\n')))

    # Get the Tag model objects for each tag (or create if they don't already exist in the Tag model)
    new_public_tags = set([Tag.objects.get_or_create(tag=tag)[0] for tag in public_tags])
    new_private_tags = set([Tag.objects.get_or_create(tag=tag)[0] for tag in private_tags])

    # Get the Item model object (or create it if it doesn't already exist in the Item model)
    item = Item.objects.get_or_create(item_id=item_id)

    # Check if user already has tags for this item
    user_contrib = UserContribution.objects.filter(user=user, item=item)
    if user_contrib.exists():
        user_contrib = user_contrib[0]

        existing_public_tags = set(user_contrib.public_tags.all())
        existing_private_tags = set(user_contrib.private_tags.all())

        public_tags_to_add = new_public_tags - existing_public_tags
        private_tags_to_add = new_private_tags - existing_private_tags
        user_contrib.public_tags.add(*public_tags_to_add)
        user_contrib.private_tags.add(*private_tags_to_add)

        # If user already has tags, but the item is being unpinned or is CURRENTLY unpinned
        # (meaning user is re-pinning an item that they previously tagged)
        # Do NOT override previous tags --> Only override if user is changing the tags on an item that's already pinned
        # + they are NOT unpinning the item
        if user_contrib.is_pinned and eval(tags_data.get('is_pinned')):
            public_tags_to_remove = existing_public_tags - new_public_tags
            private_tags_to_remove = existing_private_tags - new_private_tags
            user_contrib.public_tags.remove(*public_tags_to_remove)
            user_contrib.private_tags.remove(*private_tags_to_remove)

        user_contrib.is_pinned = eval(tags_data.get('is_pinned'))
        user_contrib.points_earned = tags_data.get('total_points_for_item')  # TODO: Add a check to make sure points_earned cannot ever decrease?
        user_contrib.save()
    else:
        user_contrib = UserContribution(user=user, item_id=item_id,
                                        is_pinned=eval(tags_data.get('is_pinned')),
                                        points_earned=tags_data.get('total_points_for_item'))
        user_contrib.save()
        user_contrib.public_tags.add(*new_public_tags)
        user_contrib.private_tags.add(*new_private_tags)


def create_tag_report(user, item_id, report_data):
    """View for tag reporting"""
    reported_tag = report_data['reported_tag']
    is_irrelevant = report_data['is_irrelevant']
    is_vulgar = report_data['is_vulgar']
    is_offensive = report_data['is_offensive']
    is_misinformation = report_data['is_misinformation']
    is_other = report_data['is_other']
    other_text = report_data['other_text']

    # Set reason for the report
    reason = next((r for r, selected in [
        ('Irrelevant', is_irrelevant),
        ('Vulgar', is_vulgar),
        ('Offensive', is_offensive),
        ('Misinformation', is_misinformation),
        ('Other', is_other),
    ] if selected), None)
    if other_text:  # If other_text is not empty
        reason += other_text

    item = Item.objects.get(item_id=item_id)
    tag = Tag.objects.get(tag=reported_tag)

    # If tag whitelisted globally or for item --> do not create report
    if tag.global_whitelist or item in tag.item_whitelist.all():
        return

    # Create the report in the database
    report = Report(item_id=item, user_id=user, tag=tag, reason=reason)
    report.save()


@receiver(post_migrate)
def set_global_blacklist(sender, **kwargs):  # pylint: disable=unused-argument
    """Function for creating the list of globally-blacklisted tags in the database automatically after db is created"""
    if sender.name == 'tagme':
        for word in GLOBAL_BLACKLIST:
            Tag.objects.get_or_create(tag=word, global_blacklist=True)


@receiver(post_migrate)
def set_reward_list(sender, **kwargs):  # pylint: disable=unused-argument
    """Function for creating the list of reward titles in the database automatically after db is created"""
    if sender.name == 'tagme':
        points_required = 10
        for title in REWARD_LIST:
            hex_colour = REWARD_LIST.get(title)
            Reward.objects.get_or_create(title=title, hex_colour=hex_colour, points_required=points_required)
            points_required += 50


# Automatically set global blacklist & rewards if database already exists (i.e., already migrated)
if "tagme_tag" in connection.introspection.table_names():
    set_global_blacklist(sender=TagMeConfig)

if "tagme_reward" in connection.introspection.table_names():
    set_reward_list(sender=TagMeConfig)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """Use Django signals to automatically create a user profile points when a user is created (admin and not)"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserContribution)
def update_user_profile_points_on_save(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Use Django signals to automatically update user profile points when a user contribution is added/updated"""
    user_profile = UserProfile.objects.get(user=instance.user)
    user_profile.update_points()


@receiver(post_delete, sender=UserContribution)
def update_user_profile_points_on_delete(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Use Django signals to automatically update user profile points when a user contribution is deleted
    NOTE: UserContributions shouldn't ever be deleted (unless the user exercises their right to be forgotten)
    """
    user_profile = UserProfile.objects.get(user=instance.user)
    user_profile.update_points()

# pylint: enable=no-member


########################################################################################################################
# DATAMUSE API QUERIES


def query_datamuse_synonyms(word):
    """Function for synonyms of a given word (may or may NOT exist as tags in our database)"""
    return list(f"placeholder code {word}")


def query_datamuse_related_words(word):
    """Function for words related to a given word (may or may NOT exist as tags in our database)"""
    return list(f"placeholder code {word}")


########################################################################################################################
# LOC API QUERIES

def query_loc_keyword(search_string, requested_page_number):
    """Keyword search to LOC API"""
    params = {
        "q": search_string,  # Default parameters set in _query_loc_api() function
        "fa": "partof:catalog"
    }
    return _query_loc_api(params, requested_page_number)


def query_loc_title(search_string, requested_page_number):
    """Title search to LOC API"""
    print(f"TODO (placeholder code) {search_string} {requested_page_number}")


def query_loc_author(search_string, requested_page_number):
    """Author search to LOC API"""
    print(f"TODO (placeholder code) {search_string} {requested_page_number}")


def query_loc_subject(search_string, requested_page_number):
    """Subject search to LOC API"""
    params = {
        "q": search_string,
        "fa": "fa=subject:"+search_string
    }
    return _query_loc_api(params, requested_page_number)


def _query_loc_api(params, requested_page_number):
    """Actual query to LOC API (PRIVATE FUNCTION)"""
    params["fa"] = "partof:catalog"
    params["fo"] = "json"
    params["c"] = 15  # Return max. 15 items per query (makes results load faster)
    params["sp"] = requested_page_number

    query = "?"
    for param_key in params.keys():
        query += param_key + "=" + quote(str(params.get(param_key)), safe=":") + "&"  # Do not encode ":" of "fa" params
    query = query[:-1]  # Remove ending "&" from query
    query_url = quote(query, safe=":?=&%")

    endpoint = "https://www.loc.gov/books/"  # API rate limit = 20 queries per 10 seconds && 80 queries per 1 minute
    try:
        response = requests.get(endpoint + query_url)
        response.raise_for_status()  # Raise an error if the request fails
        data = response.json()  # Parse the JSON response

        results_on_page = []
        for item in data.get("results", []):

            item_id = item.get('number_lccn')[0]
            title = decode_unicode(strip_punctuation(item.get("item").get('title', 'No title available')))
            publication_date = decode_unicode(item.get('date', 'No publication date available'))
            description = decode_unicode('\n'.join(item.get('description', 'No description available')))

            authors = item.get('contributor', ['Unknown'])
            for i in range(len(authors)):
                authors[i] = decode_unicode(to_firstname_lastname(authors[i]))

            covers = item.get('image_url', None)
            cover = covers[0] if covers else None

            results_on_page.append({
                'item_id': item_id,
                'title': to_title_case(title),
                'authors': to_title_case('; '.join(authors)),  # Combine authors into a single string
                'publication_date': publication_date,
                'description': description,
                'cover': cover,
            })

        return results_on_page, data.get("pagination")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return [], 0


# Comprehension is actually necessary, or Django crashes
__all__ = [name for name in globals()]  # pylint: disable=unnecessary-comprehension
__all__.remove('_query_loc_api')  # Remove _query_loc_api from exportable functions (i.e., make function private)
