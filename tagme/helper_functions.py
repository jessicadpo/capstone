"""Module for miscellaneous helper functions (mostly string manipulations & processing)"""
import html
import re
import string


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

def normalize_string(full_string):
    """Normalize a string by removing punctuation and splitting it into components"""
    full_string = re.sub(r'[^\w\s]', '', full_string)
    return set(full_string.lower().split())

def is_string_match(query_string, reference_string):
    """
    check if any component of the search string matches any component of the
    another string, no matter the order.
    """
    normalized_search = normalize_string(query_string)
    # print("strmatchfunction input: ", normalized_search) # debugging
    normalized_reference = normalize_string(reference_string)
    # print("strmatchfunction reference: ", normalized_reference) # debugging
    return (
            normalized_search.issubset(normalized_reference) or
            normalized_reference.issubset(normalized_search) or
            normalized_search == normalized_reference
    )