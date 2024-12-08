# pylint: disable=no-member
"""
Module for querying models AND Library of Congress & Datamuse APIs

RATE LIMIT FOR LIBRARY OF CONGRESS API: 20 queries per 10 seconds && 80 queries per 1 minute
"""
from urllib.parse import quote
from django.db.models import Count
from django.contrib.auth import PermissionDenied
import requests
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


def get_synonymous_tags(search_string):
    """Function for getting tags that are synonyms of a list of given words"""
    # TODO: Parse AND/OR/NOT

    synonyms = query_datamuse_synonyms(search_string)
    synonymous_tags = []
    for synonym in synonyms:
        synonym_tag = Tag.objects.filter(tag=synonym)
        if synonym_tag.exists():
            # Need to format it as a dict to stay consistent with return format of get_all_tags_for_item()
            synonymous_tags.append({"tag" : synonym_tag[0].tag})

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
        public_tags_to_remove = existing_public_tags - new_public_tags
        private_tags_to_add = new_private_tags - existing_private_tags
        private_tags_to_remove = existing_private_tags - new_private_tags

        user_contrib.public_tags.add(*public_tags_to_add)
        user_contrib.public_tags.remove(*public_tags_to_remove)
        user_contrib.private_tags.add(*private_tags_to_add)
        user_contrib.private_tags.remove(*private_tags_to_remove)

        user_contrib.is_pinned = True
        user_contrib.save()
    else:
        user_contrib = UserContribution(user=user, item_id=item_id, is_pinned=True)
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

    # if tag Whitelisted, ignore report
    if tag.global_whitelist or item in tag.item_whitelist.all():
        return

    # Create the report in the database
    report = Report(item_id=item, user_id=user, tag=tag, reason=reason)
    report.save()


def set_global_blacklist():
    """Function that returns true if the search string is blacklisted"""
    for word in GLOBAL_BLACKLIST:
        Tag.objects.get_or_create(tag=word, global_blacklist=True)


set_global_blacklist()


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
    print(f"TODO (placeholder code)) {search_string} {requested_page_number}")


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
