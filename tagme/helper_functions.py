"""Module for miscellaneous helper functions (mostly string manipulations & processing)"""
import html
import re
import string

from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string



########################################################################################################################
# HELPER FUNCTIONS FOR queries.py

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
    """Get the value to use in .order_by() when sorting UserContribution objects"""
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
    """Get all Django Q objects to pass into .filter() and .exclude() when filtering UserContribution objects"""
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


########################################################################################################################
# HELPER FUNCTIONS FOR views.py

def get_item_from_session(request, item_id=None):
    """
    Function for retrieving the data for a particular item from the user's session
    (list of items previously stored in session by Search Results or Pinned Items view).
    - If item_id is not specified, item will be retrieved from request's POST data (if specified in POST data).
    - If item_id NOT given NOR in request.POST --> returns None.
    """
    items_in_session = request.session.get('results_from_referrer', {})
    if item_id is not None:
        return items_in_session.get(str(item_id))
    if "tagged_item" in request.POST:
        return items_in_session.get(str(request.POST['tagged_item']))
    return None


def is_default_sort_and_filter(get_request):
    """
    Check whether GET request only contains default sorting && no filters
    for pages sorting & filtering UserContribution objects (e.g., Pinned Items page)
    """
    sort_by_filter = get_sort_by_filter(get_request)
    filter_query, exclude_query, tag_include_queries = get_pinned_items_filters(get_request)
    if (sort_by_filter == '-pin_datetime' and
            not filter_query.children and
            not exclude_query.children and
            len(tag_include_queries) == 0):
        return True
    return False


def paginate(request, to_paginate, template_name, page_forms, item_data=None, page_number=1):
    """
    Function for paginating content into pages of 15 items/things
    - If AJAX request --> will return the requested page.
    - If not --> will return page 1.
    """
    if to_paginate is None:
        to_paginate = []

    current_page = Paginator(to_paginate, 15).get_page(page_number)

    # If AJAX request (i.e., page already loaded)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        full_page_html = render_to_string(template_name,
                                          {'item_data': item_data, 'forms': page_forms, 'current_page': current_page},
                                          request)
        return extract_paginated_html(full_page_html)

    # IF NOT AJAX request (i.e., page loading for the first time)
    return current_page


def extract_paginated_html(full_page_html):
    """Function for getting only the HTML that needs to be changed when changing Pagination page (not web/URL page)"""
    html_parser = BeautifulSoup(full_page_html, 'html.parser')
    paginated_content_html = html_parser.find_all('div', class_="paginated-content")
    return str(paginated_content_html[0])


def parse_search_string(search_string):
    """Function for dividing a search string into different kinds of terms"""
    terms = search_string.split()
    include_terms = [term.lower() for term in terms if not term.startswith("-") and term != "-"]
    exclude_terms = [term.lstrip("-").lower() for term in terms if term.startswith("-") and term != "-"]

    return include_terms, exclude_terms

def search_results_filtering(unfiltered_results, target_category, include_terms, exclude_terms):
    """
    Function for filtering a list of search results items to those which include and exclude certain terms
    unfiltered_results must be a list of items (see results_on_page in _query_loc_api in queries.py)
    target_category must correspond to one of the keys for a results_on_page items' string-based values
    include_terms and exclude_terms must be lists of strings that do not contain whitespace characters
    """
    filtered_results = []
    for item in unfiltered_results:
        print('checking: ', item.get('item_id'))
        print(target_category, ': ', item.get(target_category))
        lower_category = item.get(target_category).lower()  # Lowercase the title so that matching is easy
        print('lowered to: ', lower_category)

        # Boolean, true if the title has all include terms
        include_check = all(term.lower() in lower_category for term in include_terms)
        if include_check:
            print('item: ', item.get('item_id'), ' passed include check')
        if not include_check:
            print('item: ', item.get('item_id'), ' failed include check')

        # Boolean, true if the title has none of the exclude terms
        exclude_check = not any(term.lower() in lower_category for term in exclude_terms)
        if exclude_check:
            print('item: ', item.get('item_id'), ' passed exclude check')
        if not exclude_check:
            print('item: ', item.get('item_id'), ' failed exclude check')

        if include_check and exclude_check:
            filtered_results.append(item)
            print('item added to filtered_results')

    return filtered_results
