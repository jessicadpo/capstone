# pylint: disable=no-member
"""
Module for querying models AND Library of Congress & Datamuse APIs

RATE LIMIT FOR LIBRARY OF CONGRESS API: 20 queries per 10 seconds && 80 queries per 1 minute
"""
from datetime import datetime
from collections import Counter
from urllib.parse import quote
import requests

from django.utils.timezone import localtime
from django.db import transaction
from django.db.models import Count
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, post_migrate
from django.forms.models import model_to_dict
from django.contrib.auth import PermissionDenied
from django.dispatch import receiver
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


def get_filtered_user_pinned_items(user, get_request):
    """
    Function for getting the items currently pinned (i.e., pinned=True) by a particular user
    that fit the filters selected by the user (i.e., in the GET request).
    - Returned items are organized in the same format used by Search Results page.
    """
    sort_by_filter = get_sort_by_filter(get_request)
    filter_query, exclude_query, tag_include_queries = get_pinned_items_filters(get_request)

    # Get only the user's current pins
    user_contribs = UserContribution.objects.filter(user_id=user.id, is_pinned=True)
    if user_contribs.exists():

        # Add count of public_tags and private_tags to every UserContribution object in user_contribs
        user_contribs_with_tag_counts = user_contribs.annotate(public_tag_count=Count('public_tags'),
                                                               private_tag_count=Count('private_tags'))

        # Apply filters & sorting to user's pins
        filtered_user_contribs = (user_contribs_with_tag_counts
                                  .filter(filter_query)
                                  .exclude(exclude_query)
                                  .distinct()
                                  .order_by(sort_by_filter))

        for tag_filter_query in tag_include_queries:
            filtered_user_contribs = filtered_user_contribs.filter(tag_filter_query)

        # Convert UserContribution objects into a dict with the same format as used by Search Results page
        # (Necessary for proper insertion into item_result.html)
        user_pins = []
        for pin in filtered_user_contribs:
            pinned_item = model_to_dict(pin.item)
            pinned_item.pop('_subjects')  # Remove subjects formatted as a single string
            pinned_item['subjects'] = pin.item.subjects  # Add subjects formatted in a list

            user_public_tags, user_private_tags = get_user_tags_for_item(user, pin.item.item_id)
            pinned_item['user_public_tags'] = user_public_tags
            pinned_item['user_private_tags'] = user_private_tags
            pinned_item['is_pinned'] = pin.is_pinned
            pinned_item['date_pinned'] = localtime(pin.pin_datetime).strftime('%Y-%m-%d %H:%M%p') if pin.pin_datetime is not None else "Date unavailable"
            pinned_item['points_earned'] = pin.points_earned

            user_pins.append(pinned_item)

        # Returning filtered_user_contribs as well for get_[thing]_with_item_counts() functions
        return user_pins, filtered_user_contribs
    return [], None


def get_5_most_frequent_user_tags(user):
    """
    Function for getting the 5 most frequently-used tags across a user's pinned items
    (NO FILTERS except is_pinned=True are applied).
    - If two items have the same frequency --> In alphabetical order
    - Returns a list of strings (each string = a tag's text value)

    NOTE: tag_count != item_count.
    - Tag count == the number of times a user has used a tag. It's possible
      for a user to use the same tag on an item twice (once as a public tag, and again as a private tag).

    - Item count == the number of unique items the user has used a given tag
      on. This count is calculated by a different function (not this one).
    """
    user_contribs = UserContribution.objects.filter(user_id=user.id, is_pinned=True)

    if user_contribs.exists():
        public_tag_counts = user_contribs.values("public_tags__tag").annotate(tag_count=Count("public_tags__tag"))
        private_tag_counts = user_contribs.values("private_tags__tag").annotate(tag_count=Count("private_tags__tag"))

        # private/public_tag_counts are lists of dicts where each dict is {'public_tags__tag': 'tag_text', 'tag_count': integer}
        # Need to sum the counts across public & private counts
        # & convert this into a list of dicts where each dict is {'tag_text': integer}
        public_tag_counts = Counter({item["public_tags__tag"]: item["tag_count"] for item in public_tag_counts if item["public_tags__tag"]})
        private_tag_counts = Counter({item["private_tags__tag"]: item["tag_count"] for item in private_tag_counts if item["private_tags__tag"]})
        total_tag_counts = public_tag_counts + private_tag_counts

        # Sort tags based on tag_count (i.e., 2nd element of each key-value pair) from largest to smallest,
        # then alphabetically (i.e., smallest to largest) for tags with the same count
        tag_counts = sorted(total_tag_counts.items(), key=lambda x: (-x[1], x[0]))

        # NOTE: tag frequency is determined by tag_count, but the number displayed in the front-end is item_count
        # so tags with the same item_count may NOT be in alphabetical order if they have different tag_counts.
        # We show item_count instead of tag_count in the front-end because it's more relevant for the user to know
        # how many items will be returned by that particular filter rather than knowing how many times they used a tag.

        # Extract the 5 most frequent tags & only store their text value
        five_most_frequent_tags = [list(tag_set)[0] for tag_set in tag_counts[:5]]

        return list(filter(None, five_most_frequent_tags))  # Remove empty strings, if there are any
    return None


def get_5_most_frequent_user_tags_with_item_counts(user, filtered_contribs):
    """
    Function for getting number of times each of the 5 most frequently-used tags were used on a unique item
    within a given set of FILTERED pinned items.
    - Returns a list of dicts in {'tag': 'tag_text', 'item_count': integer} format

    NOTE: tag_count != item_count.
    - Tag count == the number of times a user has used a tag. It's possible
      for a user to use the same tag on an item twice (once as a public tag, and again as a private tag).
      This count is calculated by a different function (not this once).

    - Item count == the number of unique items the user has used a given tag on.
    """
    if filtered_contribs is None:  # Don't bother checking for frequent tags if user has made 0 pins
        return None

    most_frequent_tags = get_5_most_frequent_user_tags(user)

    frequent_tags_with_item_counts = []

    for tag in most_frequent_tags:
        if filtered_contribs.exists():
            item_count_for_tag = (filtered_contribs
                                  .filter(Q(public_tags__tag__iexact=tag) | Q(private_tags__tag__iexact=tag))
                                  .distinct()
                                  .count())
            frequent_tags_with_item_counts.append({'tag': tag, 'item_count': item_count_for_tag})
        else:  # Default counts for all frequent tags == 0
            frequent_tags_with_item_counts.append({'tag': tag, 'item_count': 0})
    return frequent_tags_with_item_counts


def get_user_contribution_types_with_item_counts(user, filtered_contribs):
    """
    Function for getting the item_counts to append to each "Your Contributions" filter in the Pinned Items page.
    - Each item_count represents the number of pinned items in a given set of contributions for a
      particular user and type of contribution.
    - Types of contributions: Public Tags, Private Tags, Comments
    - If no contributions given --> returns the item_counts across all of the user's contributions
      (no filters except is_pinned=True are applied).
    """
    if filtered_contribs is None:
        filtered_contribs = UserContribution.objects.filter(user_id=user.id, is_pinned=True)

    if filtered_contribs.exists():
        item_count_with_public_tags = (filtered_contribs
                                       .annotate(count=Count('public_tags'))
                                       .filter(count__gt=0)
                                       .count())

        item_count_with_private_tags = (filtered_contribs
                                        .annotate(count=Count('private_tags'))
                                        .filter(count__gt=0)
                                        .count())

        item_count_with_comments = (filtered_contribs
                                    .exclude(comment__isnull=True)
                                    .exclude(comment="")
                                    .count())

        return item_count_with_public_tags, item_count_with_private_tags, item_count_with_comments
    return 0, 0, 0


def get_all_tags_for_item(item_id):
    """Function for getting all tags for a particular item_id"""
    item = Item.objects.filter(item_id=item_id)
    if item.exists():
        # Return an array of dicts, each dict contains a tag and its count
        # Exclude globally-blacklisted tags
        item_public_tags_with_counts = (Tag.objects
                                        .filter(public_tags__item_id=item_id, global_blacklist=False)
                                        .exclude(item_blacklist__item_id=item_id)
                                        .annotate(count=Count('public_tags'))
                                        .order_by('-count'))
        all_tags_for_item = []
        for tag in item_public_tags_with_counts:
            tag_dict = {'count': tag.count, 'tag': tag.tag}
            all_tags_for_item.append(tag_dict)

        return all_tags_for_item
    return None


def get_user_tags_for_item(user, item_id):
    """
    Function for retrieving a user's tags for a particular item.
    - Returns 2 lists of {'tag': tag_value} dicts.
    - Using dicts instead of simple strings so that other tag_related data can be bundled with the
      tag (e.g., usage count) if need be.
    """
    if not user.is_authenticated:
        raise PermissionDenied("User must be logged in")

    # Returns a list of dicts (each tag in its own dict)
    user_contrib = UserContribution.objects.filter(user_id=user.id, item_id=item_id)
    if user_contrib.exists():
        user_contrib = user_contrib[0]
        user_public_tags = list(user_contrib.public_tags.all().values('tag'))
        user_private_tags = list(user_contrib.private_tags.all().values('tag'))
        return user_public_tags, user_private_tags
    return None, None


def get_all_comments_for_item(item_id, user=None):
    """Function for getting all comments for a particular item_id"""
    item = Item.objects.filter(item_id=item_id)
    if item.exists():
        # Exclude contributions with 0 comments
        comment_contributions = (UserContribution.objects
                                 .filter(item_id=item_id)
                                 .exclude(comment__isnull=True)
                                 .order_by('comment_datetime'))

        # Exclude the comment of the user making the request
        if user is not None and user.is_authenticated:
            comment_contributions = comment_contributions.exclude(user=user)

        # Return an array of dicts, each dict contains:
        # comment's text, comment_datetime, contributing user's username, contributing user's equipped titles
        comments = []
        for contrib in comment_contributions:
            equipped_1, equipped_2 = get_equipped_titles(contrib.user)
            comment = {'paragraphs': contrib.comment.split('\r\n\r\n'),
                       'datetime': localtime(contrib.comment_datetime).strftime('%B %d, %Y %H:%M %p'),
                       'username': contrib.user.username,
                       'equipped_title_1': equipped_1,
                       'equipped_title_2': equipped_2}
            comments.append(comment)

        # Re-add the comment of the user making the request (if there is one) to the start of the list
        # to ensure that it's always the first comment shown in the front-end
        user_comment = get_user_comment_for_item(user, item_id)
        if user_comment:
            comments.insert(0, user_comment)

        return comments
    return None


def get_user_comment_for_item(user, item_id):
    """Function for retrieving a user's comment for a particular item"""
    if not user.is_authenticated:
        return None

    user_contrib = UserContribution.objects.filter(user_id=user.id, item_id=item_id)
    if user_contrib.exists() and user_contrib[0].comment is not None:
        equipped_1, equipped_2 = get_equipped_titles(user)
        comment = {'paragraphs': user_contrib[0].comment.split('\r\n\r\n'),
                   'datetime': localtime(user_contrib[0].comment_datetime).strftime('%B %d, %Y %H:%M %p'),
                   'username': user.username,
                   'equipped_title_1': equipped_1,
                   'equipped_title_2': equipped_2}
        return comment
    return None


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
            equipped_title_1 = reward_to_dict_format(equipped_title_1_object[0])

        if equipped_title_2_object.exists():
            equipped_title_2 = reward_to_dict_format(equipped_title_2_object[0])

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


def get_synonymous_tags(include_terms):
    """Function for getting (non-blacklisted) tags that are synonyms of a list of given words"""
    returned_synonymous_tags = []
    if len(include_terms) > 0:
        # NOTE: Do NOT need to include the different forms of each synonym since
        # tag search already includes all the forms in the search results
        # e.g., "boat" and "boats" tags return the exact same search results
        synonyms = query_datamuse_synonyms(' '.join(include_terms))

        # Get all the Tags that match one of the synonyms in their tag value (case-insensitive)
        if len(synonyms) > 0:
            query = Q()
            for synonym in synonyms:
                query |= Q(tag__iexact=synonym)
            query &= Q(global_blacklist=False)
            query &= Q(public_tags__isnull=False)  # Must exist as public tags
            synonymous_tags = Tag.objects.filter(query).distinct()

            if synonymous_tags.exists():
                for synonymous_tag in synonymous_tags:
                    if len(returned_synonymous_tags) < 20: # Return max. 20 synonyms
                        # Need to format it as a dict to stay consistent with return format of get_all_tags_for_item()
                        returned_synonymous_tags.append({"tag": synonymous_tag.tag})
    return returned_synonymous_tags


def get_related_tags(include_terms, filtered_results, synonymous_tags):
    """
    Function for getting (non-blacklisted) tags that are related to a list of given words.
    This includes:
    - Public tags that have been applied to the returned search results
      AND (if haven't reached 20-tag limit yet)
    - Any words returned by Datamuse API that also exist as tags in database
    It EXCLUDES:
    - Tags that are already in the Synonymous Tags list
    """
    # Get the public tags for all the items in the filtered results
    # and count on how many items each tag has been used (within the filtered_results)
    #TODO: What if more than 20 related tags?
    tags_in_results = {}
    for item in filtered_results:
        item_public_tags = get_all_tags_for_item(item['item_id'])
        if item_public_tags is not None:
            for public_tag in item_public_tags:
                tag = public_tag['tag']
                item_count = tags_in_results[tag] + 1 if tag in tags_in_results else 1
                tags_in_results[tag] = item_count

    # Sort tags from biggest item_count to smallest item_count
    # and only keep the first 20
    sorted_tags = (sorted(tags_in_results.items(), key=lambda tag: tag[1], reverse=True))[:20]
    returned_related_tags = [{"tag": key, "item_count": value} for key, value in sorted_tags]

    # Only query datamuse for related terms if still don't have 20 tags in returned_related_tags
    if len(returned_related_tags) < 20:
        related_words = query_datamuse_related_words(' '.join(include_terms))

        # Get all the Tags that include at least one of the related_words in their tag value (case-insensitive)
        if len(related_words) > 0:
            query = Q()
            for rel_word in related_words:
                query |= Q(tag__icontains=rel_word)
            query &= Q(global_blacklist=False)
            query &= Q(public_tags__isnull=False)  # Must exist as public tags
            related_tags = Tag.objects.filter(query)

            if related_tags.exists():
                for related_tag in related_tags:
                    if len(returned_related_tags) < 20:
                        # Need to format it as a dict to stay consistent with return format of get_all_tags_for_item()
                        returned_related_tags.append({"tag": related_tag.tag})

    # Exclude any related_tag that is an exact match to any of the include_terms & their different forms
    include_forms_per_term = singularize_pluralize_words(include_terms)
    include_all_terms = {form for term in include_forms_per_term for form in term.values()}
    returned_related_tags = [tag for tag in returned_related_tags if tag['tag'] not in include_all_terms]

    # Exclude any related_tag that is an exact match to the entire search string
    include_search_string = ' '.join(include_terms)
    returned_related_tags = [tag for tag in returned_related_tags if tag['tag'] != include_search_string]

    # Exclude any related_tag that is already in synonymous tags or a different form of a synonymous tag
    synonyms = [syn_tag["tag"] for syn_tag in synonymous_tags]
    forms_per_synonym = singularize_pluralize_words(synonyms)
    synonyms = {form for term in forms_per_synonym for form in term.values()}
    returned_related_tags = [tag for tag in returned_related_tags if tag['tag'] not in synonyms]

    # Remove duplicates while also preserving the order
    first_occurrences = set()
    unique_returned_tags = []
    for tag in returned_related_tags:
        if tag['tag'] not in first_occurrences:
            first_occurrences.add(tag['tag'])
            unique_returned_tags.append(tag)

    return unique_returned_tags


def remove_globally_banned_tags_from_tag_search(search_string):
    """
    Function for removing globally banned TAGS (not subject headings, titles, etc.) from search string.
    Returns a search_string without the banned tags, so now TAG searches will exclude items with that tag.
    """
    banned_tags = set(Tag.objects.filter(global_blacklist=True).values_list('tag', flat=True))
    regex_pattern = r"|".join(map(re.escape, banned_tags))
    cleaned_search_string = re.sub(regex_pattern, "", search_string)  # Replace all banned terms with an empty string
    return cleaned_search_string


def get_tag_search_results(include_terms=None, exclude_terms=None):
    """Get the items that match the include and exclude search terms for a Tag search"""
    filtered_items = []
    if include_terms:
        # Plurality control (all tags regardless of plural or singular form)
        # NOT pluralizing/singularizing exclude_tags to allow users to include one form, but exclude another
        # (e.g., can search "vampire -vampires" if they so wish, for some reason)
        include_forms_per_term = singularize_pluralize_words(include_terms)
        include_all_terms = {form for term in include_forms_per_term for form in term.values()}

        # Get all the Tags that include at least one of the include_terms in their tag value (case-insensitive)
        query = Q()
        for include_term in include_all_terms:
            query |= Q(tag__icontains=include_term)
        include_tags = Tag.objects.filter(query)

        # Get all the items that have at least one of the include_terms in its public_tags
        user_contributions = UserContribution.objects.filter(Q(public_tags__tag__in=include_tags)).distinct()
        items = Item.objects.filter(item_id__in=user_contributions.values_list('item_id', flat=True)).distinct()

        # Make sure only items whose public_tags that contain ALL of the include_terms are returned
        # (since ' ' == AND operator)
        for item in items:
            item_public_tags = [dictionary["tag"] for dictionary in get_all_tags_for_item(item.item_id)]

            # Convert all tags to lowercase for case-insensitive comparison
            # Use set for efficiency
            item_public_tags = [tag.lower() for tag in item_public_tags]

            # Check if ALL include_terms (in at least one of their singular/plural forms)
            # are found in the item's public tags
            if all(any(any(form.lower() in tag for tag in item_public_tags) for form in term.values()) for term in include_forms_per_term):
                filtered_items.append(item)

        # Convert filtered_items into a queryset
        item_ids = [item.item_id for item in filtered_items]
        filtered_items = Item.objects.filter(item_id__in=item_ids)
    else:
        filtered_items = Item.objects.all()

    # Multiple "NOT" relationships are treated as OR relationships (not AND), even if space is supposed to be AND operator
    # (e.g., "-vampires -werewolves" excludes items tagged "vampires" only, "werewolves" only,
    # AND items tagged both "vampires" and "werewolves", not just the items that have both tags)
    if exclude_terms:
        # Get all the Tags that include at least one of the exclude_terms in their tag value (case-insensitive)
        query = Q()
        for exclude_term in exclude_terms:
            query |= Q(tag__icontains=exclude_term)
        excluded_tags = Tag.objects.filter(query)
        excluded_link = UserContribution.objects.filter(Q(public_tags__tag__in=excluded_tags)).distinct()
        excluded_items = Item.objects.filter(item_id__in=excluded_link.values_list('item_id', flat=True)).distinct()
        filtered_items = filtered_items.exclude(item_id__in=excluded_items.values_list('item_id', flat=True))

    # If filtered_items is still a list --> Convert filtered_items into a queryset
    if isinstance(filtered_items, list):
        item_ids = [item.item_id for item in filtered_items]
        filtered_items = Item.objects.filter(item_id__in=item_ids)

    return list(filtered_items.values())


#######################################################
# SETTERS
def set_item(item_data):
    """
    Function for storing item data (from LOC API) into TagMe model for later retrieval (i.e., Pinned Items
    page) & minimizing API calls (due to rate limits)
    """
    # Check if item has already been saved to TagMe database
    item = Item.objects.filter(item_id=item_data['item_id'])
    if item.exists():
        item = item[0]
        # Fill-in any missing information for items created before Item model's update
        if item.title != item_data['title']:
            item.title = item_data['title']
            item.author = item_data['authors']
            item.publication_date = item_data['publication_date']
            item.description = item_data['description']
            item.subjects = item_data['subjects']
            item.cover = item_data['cover']
            item.save()
    else:
        item = Item(item_id=item_data['item_id'], title=item_data['title'], authors=item_data['authors'],
                    publication_date=item_data['publication_date'], description=item_data['description'],
                    subjects=item_data['subjects'], cover=item_data['cover'])
        item.save()


def set_equipped_title(user, equip_form):
    """Function for equipping/unequipping titles"""
    title_to_equip = equip_form.cleaned_data.get('title_to_equip')
    slot = equip_form.cleaned_data.get('equip_slot')  # Can be '1' or '2'
    user_profile = UserProfile.objects.filter(user=user)[0]
    equipped_title_1, equipped_title_2 = get_equipped_titles(user)

    if slot == '1':
        if title_to_equip == "Empty":
            user_profile.equipped_title_1 = None  # Unequip title
        elif equipped_title_1 is not None and title_to_equip == equipped_title_1.get('title'):
            return
        else:
            user_profile.equipped_title_1 = Reward.objects.filter(title=title_to_equip)[0]
    else:
        if title_to_equip == "Empty":
            user_profile.equipped_title_2 = None  # Unequip title
        elif equipped_title_2 is not None and title_to_equip == equipped_title_2.get('title'):
            return
        else:
            user_profile.equipped_title_2 = Reward.objects.filter(title=title_to_equip)[0]

    user_profile.save()


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

    # Check if user already has tags/a comment for this item
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
        user_contrib.points_earned = tags_data.get('total_points_for_item')
        user_contrib.save()
    else:
        user_contrib = UserContribution(user=user, item_id=item_id,
                                        is_pinned=eval(tags_data.get('is_pinned')),
                                        points_earned=tags_data.get('total_points_for_item'))
        user_contrib.save()
        user_contrib.public_tags.add(*new_public_tags)
        user_contrib.private_tags.add(*new_private_tags)


def set_user_comment_for_item(user, item_id, comment_data):
    """Function for adding/updating a user's comment for a particular item"""
    # Get the Item model object (or create it if it doesn't already exist in the Item model)
    item = Item.objects.get_or_create(item_id=item_id)

    # Check if user already has tags/a comment for this item
    user_contrib = UserContribution.objects.filter(user=user, item=item)
    if user_contrib.exists():
        user_contrib = user_contrib[0]
        user_contrib.comment = comment_data.get('comment')
        user_contrib.save_comment()
    else:
        user_contrib = UserContribution(user=user, item_id=item_id, comment=comment_data.get('comment'))
        user_contrib.save_comment()


def delete_user_comment_for_item(user, item_id):
    """Function for delete a user's comment for a particular item"""
    # Get the Item model object
    item = Item.objects.filter(item_id=item_id)[0]

    # Check if user already has tags/a comment for this item
    # (they should, if they were able to request a comment delete)
    user_contrib = UserContribution.objects.filter(user=user, item=item)
    if user_contrib.exists():
        user_contrib = user_contrib[0]
        user_contrib.comment = None
        user_contrib.save_comment()  # Save the time the comment was deleted


def create_tag_report(user, item_id, report_data):
    """Function for creating a tag report"""
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
    ] if selected), "No reason given.")
    if other_text:  # If other_text is not empty
        reason += ". " + other_text

    item = Item.objects.get(item_id=item_id)
    tag = Tag.objects.get(tag=reported_tag)

    # Create the report in the database
    report = Report(item_id=item, user_id=user, tag=tag, reason=reason)

    # If tag whitelisted globally or for item --> auto-set decision to "Ignore Report"
    if tag.global_whitelist or item in tag.item_whitelist.all():
        report.decision = Report.ReportDecision.IGNORE_REPORT
        report.decision_datetime = datetime.now()

    report.save()


def delete_user(user):
    """
    Function for deleting a User object from the database
    Note: Related objects in other models are automatically deleted via on_delete=models.CASCADE or Django signals
    """
    user.delete()


def update_tag_lists(updated_report, simulation=False, pre_save_report_id=None):
    """
    Function for updating the banlist/allowlist of a tag based on a particular report.
    - If simulation is True, the tag will not actually be updated in the database
    - If simulation is True, pre_save_report_id is required because updated_report
    is not a Report object that actually exists in the database
    """
    if simulation and not Report.objects.filter(report_id=pre_save_report_id).exists():
        raise ValueError("Valid report_id is required if simulation is True.")
    if not simulation:
        pre_save_report_id = updated_report.report_id

    with transaction.atomic():
        tag = Tag.objects.filter(tag=updated_report.tag.tag)[0]

        match updated_report.decision:
            case "global_blacklist":
                tag.global_blacklist = True
                tag.global_whitelist = False
                tag.item_whitelist.remove(updated_report.item_id)
            case "global_whitelist":
                tag.global_blacklist = False
                tag.global_whitelist = True
                tag.item_blacklist.remove(updated_report.item_id)
            case "item_blacklist":
                tag.global_whitelist = False
                tag.item_blacklist.add(updated_report.item_id)
                tag.item_whitelist.remove(updated_report.item_id)

                # Set tag's global_blacklist to False ONLY IF no longer have any reports with "global_blacklist" decision
                # or the most recent "global"-type decision for this tag is NOT "global_blacklist"
                global_decisions = (Report.objects
                                    .filter(decision__contains="global", tag=tag)
                                    .exclude(report_id=pre_save_report_id)
                                    .order_by('-decision_datetime'))

                if not global_decisions.exists() or global_decisions[0].decision != "global_blacklist":
                    tag.global_blacklist = False
                elif global_decisions[0].decision == "global_blacklist":
                    tag.global_blacklist = True

            case "item_whitelist":
                tag.global_blacklist = False
                tag.item_blacklist.remove(updated_report.item_id)
                tag.item_whitelist.add(updated_report.item_id)

                # Set tag's global_whitelist to False ONLY IF no longer have any reports with "global_whitelist" decision
                # or the most recent "global"-type decision for this tag is NOT "global_whitelist"
                global_decisions = (Report.objects
                                    .filter(decision__contains="global", tag=tag)
                                    .exclude(report_id=pre_save_report_id)
                                    .order_by('-decision_datetime'))
                if not global_decisions.exists() or global_decisions[0].decision != "global_whitelist":
                    tag.global_whitelist = False
                elif global_decisions[0].decision == "global_whitelist":
                    tag.global_whitelist = True

            case _:  # Ignore Report or null
                # Reset all the tag's blacklist/whitelist attributes
                tag.global_blacklist = False
                tag.global_whitelist = False
                tag.item_blacklist.clear()
                tag.item_whitelist.clear()

                global_decisions = (Report.objects
                                    .filter(decision__contains="global", tag=tag)
                                    .exclude(report_id=pre_save_report_id))
                item_decisions = (Report.objects
                                  .filter(decision__contains="item", tag=tag, item_id=updated_report.item_id)
                                  .exclude(report_id=pre_save_report_id)
                                  .order_by("decision_datetime"))
                all_decisions = (global_decisions | item_decisions).order_by("decision_datetime")  # From oldest to newest
                if all_decisions.exists():
                    for report in all_decisions:
                        tag = update_tag_lists(report)  # RECURSION HERE (sets tag's blacklist/whitelist attributes from previous reports)

        if simulation:
            # Need to copy item lists because ManyToMany field not actually set until .save() is called
            simulated_new_item_blacklist = list(tag.item_blacklist.values_list('item_id', flat=True))
            simulated_new_item_whitelist = list(tag.item_whitelist.values_list('item_id', flat=True))
            transaction.set_rollback(True)
            return tag, simulated_new_item_blacklist, simulated_new_item_whitelist

        # If not simulation
        tag.save()
        return tag  # Returns the updated tag


#######################################################
# SIGNALS (AUTO-SETTERS)

# Disable unused-argument pylint check for Django signals (unused arguments are necessary, even if unused)
# pylint: disable=unused-argument

@receiver(post_migrate)
def set_global_blacklist(sender, **kwargs):
    """Function for creating the list of globally-blacklisted tags in the database automatically after db is created"""
    if sender.name == 'tagme':
        for word in GLOBAL_BLACKLIST:
            Tag.objects.get_or_create(tag=word, global_blacklist=True)


@receiver(post_save, sender=Report)
def update_tag_with_report_decision(sender, instance, **kwargs):
    """Auto-trigger function for updating the banlist/allowlist of a tag when a decision is made on a report"""
    update_tag_lists(instance)


@receiver(post_migrate)
def set_reward_list(sender, **kwargs):
    """Function for creating the list of reward titles in the database automatically after db is created"""
    if sender.name == 'tagme':
        points_required = 10
        for title in REWARD_LIST:
            hex_colour = REWARD_LIST.get(title)
            Reward.objects.get_or_create(title=title, hex_colour=hex_colour, points_required=points_required)
            points_required += 60


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Use Django signals to automatically create a user profile points when a user is created (admin and not)"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserContribution)
def update_user_profile_points_on_save(sender, instance, **kwargs):
    """Use Django signals to automatically update user profile points when a user contribution is added/updated"""
    user_profile = UserProfile.objects.get(user=instance.user)
    user_profile.update_points()


@receiver(post_delete, sender=UserContribution)
def update_user_profile_points_on_delete(sender, instance, **kwargs):
    """
    Use Django signals to automatically update user profile points when a user contribution is deleted
    NOTE: UserContributions shouldn't ever be deleted (unless the user exercises their right to be forgotten)
    """
    user_profile = UserProfile.objects.get(user=instance.user)
    user_profile.update_points()


@receiver(pre_delete, sender=UserProfile)
def delete_user_contributions_on_profile_delete(sender, instance, **kwargs):
    """
    Use Django signals to automatically delete all relevant user contributions BEFORE a user profile is deleted.
    Otherwise, impossible to delete a User (website crashes instead).
    """
    UserContribution.objects.filter(user=instance.user).delete()


@receiver(pre_save, sender=UserContribution)
def update_pin_datetime(sender, instance, **kwargs):
    """Use Django signals to automatically update the datetime of a pin BEFORE a user contribution is saved."""
    if instance.pk:  # If UserContribution object already exists (this is an update, not a creation)
        old_contrib = sender.objects.get(pk=instance.pk)
        if not old_contrib.is_pinned and instance.is_pinned:  # If re-pinning an item
            instance.pin_datetime = timezone.now()
    else:
        if instance.is_pinned:  # If the new UserContribution is pinning an item (not just a comment)
            instance.pin_datetime = timezone.now()

# pylint: enable=unused-argument
# pylint: enable=no-member


########################################################################################################################
# DATAMUSE API QUERIES

def query_datamuse_synonyms(word):
    """Function for retrieving max. 50 synonyms from Datamuse API"""
    url = f"https://api.datamuse.com/words?ml={Word(word).singularize()}&max=50"
    response = requests.get(url)
    if response.status_code == 200:
        words = response.json()
        sorted_words = sorted(words, key=lambda x: x.get('score', 0), reverse=True)
        return [entry['word'] for entry in sorted_words]
    return []


def query_datamuse_related_words(word):
    """Function for retrieving max. 50 related words from Datamuse API"""
    url = f"https://api.datamuse.com/words?rel_trg={word}&max=50"
    response = requests.get(url)
    if response.status_code == 200:
        words = response.json()
        sorted_words = sorted(words, key=lambda x: x.get('score', 0), reverse=True)
        return [entry['word'] for entry in sorted_words]
    return []


########################################################################################################################
# LOC API QUERIES

def query_loc_gateway(search_string):
    """Filters requests into the API query"""
    # Note: API parses multiple keywords as ANDs for keyword search
    params = {
        "q": search_string,  # All API calls need a search string at base
    }
    return _query_loc_api(params)


def _query_loc_api(params):
    """Actual query to LOC API (PRIVATE FUNCTION)"""
    params["fa"] = "partof:catalog"
    params["fo"] = "json"
    params["c"] = 300
    params["sp"] = 1

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
            item_id = item.get('number_lccn')[0] if item.get('number_lccn') is not None else item.get('id')[item.get('id').rfind('/')+1:]
            title = decode_unicode(strip_punctuation(item.get("item").get('title', 'No title available')))
            publication_date = decode_unicode(item.get('date', 'No publication date available'))
            description = decode_unicode('\n'.join(item.get('description', 'No description available')))

            subjects = item.get('subject', [])
            for i in range(len(subjects)):
                subjects[i] = to_title_case(subjects[i])

            authors = item.get('contributor', ['Unknown'])
            for i in range(len(authors)):
                authors[i] = decode_unicode(authors[i])

            covers = item.get('image_url', None)
            cover = covers[0] if covers else None

            results_on_page.append({
                'item_id': item_id,
                'title': to_title_case(title),
                'authors': to_title_case('; '.join(authors)),  # Combine authors into a single string
                'publication_date': publication_date,
                'description': description,
                'subjects': subjects,
                'cover': cover,
            })
        return results_on_page

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return [], 0


def query_loc_single_item(item_id):
    """Function for retrieving the data of a singular item from LOC API"""
    query = "https://www.loc.gov/item/" + item_id + "/?fo=json"
    try:
        response = requests.get(query)
        response.raise_for_status()  # Raise an error if the request fails
        data = response.json()  # Parse the JSON response
        item = data.get("item")

        title = decode_unicode(strip_punctuation(item.get("item").get('title', 'No title available')))
        publication_date = decode_unicode(item.get('date', 'No publication date available'))
        description = decode_unicode('\n'.join(item.get('description', 'No description available')))

        subjects = item.get('subject', [])
        for i in range(len(subjects)):
            subjects[i] = to_title_case(subjects[i])

        authors = item.get('contributor_names', ['Unknown'])
        for i in range(len(authors)):
            authors[i] = decode_unicode(authors[i])

        covers = item.get('image_url', None)
        cover = covers[0] if covers else None

        item_data = {
            'item_id': item_id,
            'title': to_title_case(title),
            'authors': to_title_case('; '.join(authors)),  # Combine authors into a single string
            'publication_date': publication_date,
            'description': description,
            'subjects': subjects,
            'cover': cover,
         }

        return item_data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


# Comprehension is actually necessary, or Django crashes
__all__ = [name for name in globals()]  # pylint: disable=unnecessary-comprehension
__all__.remove('_query_loc_api')  # Remove _query_loc_api from exportable functions (i.e., make function private)
