"""Module for miscellaneous helper functions (mostly string manipulations & processing)"""
import html
import re
import string

from django.db.models import Q


def decode_unicode(text_string):
    """Convert any unicode to actual characters"""
    return html.unescape(text_string)


def strip_punctuation(word):
    """Remove punctuation from start and end of a string"""
    word = decode_unicode(word)
    word = word.strip("“")
    word = word.strip("”")
    return word.strip(string.punctuation)


def is_roman_numeral(word):
    """Regex pattern to match Roman numerals (uppercase or lowercase)"""
    roman_pattern = r"^[IVXLCDMivxlcdm]+$"
    return bool(re.match(roman_pattern, word))


def to_title_case(text):
    """Convert text to title case"""
    small_words = {"and", "or", "the", "in", "of", "a", "an", "to", "for", "nor", "but", "on", "at", "by", "with"}
    words = text.split()

    # Capitalize 1st word & words that aren't small words
    for i in range(len(words)):
        word_no_punctuation = strip_punctuation(words[i])
        if is_roman_numeral(word_no_punctuation):
            words[i] = words[i].upper()
        elif i == 0 or (word_no_punctuation.lower() not in small_words):
            capitalized_word = word_no_punctuation.capitalize()
            words[i] = words[i].replace(word_no_punctuation, capitalized_word)
        else:
            words[i] = words[i].lower()

    return ' '.join(words)  # Unsplit the text


def to_firstname_lastname(name):
    """Convert names containing 1 comma (Lastname, Firstname) to Firstname Lastname format"""
    if name.count(',') == 1:
        # Split the name by comma, then strip any extra spaces
        lastname, firstname = [name_part.strip() for name_part in name.split(',')]
        return f"{firstname} {lastname}"
    return name


def reward_to_dict_format(reward):
    """Convert a Reward object to a front-end readable dict format"""
    return {'title': reward.title, 'colour': reward.hex_colour, 'points_required': reward.points_required}


def get_sort_by_filter(get_request):
    if len(get_request) > 0:
        selected_sort_order = get_request['sort_order']

        if "title" in selected_sort_order:
            sort_by_filter = "item__title"
        elif "author" in selected_sort_order:
            sort_by_filter = "item__authors"
        elif "pubdate" in selected_sort_order:
            sort_by_filter = "item__publication_date"
        else:  # "pindate" in selected_sort_order / default
            sort_by_filter = "pin_datetime"

        if "za" in selected_sort_order or "no" in selected_sort_order:
            sort_by_filter = "-" + sort_by_filter
    else:
        sort_by_filter = "-pin_datetime"  # Default filter if none specified in request.GET

    return sort_by_filter


def get_pinned_items_filters(get_request):
    filter_query = Q()  # Query to be passed to the .filter() function
    exclude_query = Q()  # Query to be passed to the .exclude() function
    tag_include_queries = []  # Queries to be passed to their own .filter() function

    # Different tags to include need to be in their own .filter() function because of
    # Django weirdness in processing & (AND) operators for filtering QuerySets.
    # Does not affect tags to exclude since .exclude() logic uses | (OR) operators

    if len(get_request) > 0:
        # Add filter query for public tags (if selected by user)
        if get_request["public_tags"] == '0':  # If want to exclude items with public tags
            exclude_query |= Q(**{"public_tag_count__gt": 0})
        elif get_request["public_tags"] == '1':  # If want to include items with public tags
            filter_query &= Q(**{"public_tag_count__gt": 0})

        # Add filter query for private tags (if selected by user)
        if get_request["private_tags"] == '0':  # If want to exclude items with private tags
            exclude_query |= Q(**{"private_tag_count__gt": 0})
        elif get_request["private_tags"] == '1':  # If want to include items with private tags
            filter_query &= Q(**{"private_tag_count__gt": 0})

        # Add filter queries for comments (if selected by user)
        if get_request["comments"] == '0':  # If exclude items with comments
            # If comment is blank (""), treat it as if there's no comment
            exclude_query |= Q(comment__isnull=False) | Q(comment__exact="")
        elif get_request["comments"] == '1':  # If include items with comments
            # If comment is blank (""), treat it as if there's no comment (so EXCLUDE them in returned QuerySet)
            filter_query &= Q(comment__isnull=False)
            exclude_query |= Q(comment__exact="")

        # Create a filter query for specific tags to include (as selected by user)
        # See comment at top of function
        for tag in get_request['include_tags'].split('\\n'):
            if tag != '':
                tag_include_queries.append(Q(public_tags__tag__iexact=tag) | Q(private_tags__tag__iexact=tag))

        # Add filter queries for specific tags to exclude (as selected by user)
        for tag in get_request['exclude_tags'].split('\\n'):
            if tag != '':
                exclude_query |= Q(public_tags__tag__iexact=tag) | Q(private_tags__tag__iexact=tag)

    return filter_query, exclude_query, tag_include_queries


def is_default_sort_and_filter(get_request):
    sort_by_filter = get_sort_by_filter(get_request)
    filter_query, exclude_query, tag_include_queries = get_pinned_items_filters(get_request)
    if (sort_by_filter == '-pin_datetime' and
            not filter_query.children and
            not exclude_query.children and
            len(tag_include_queries) == 0):
        return True
    return False
