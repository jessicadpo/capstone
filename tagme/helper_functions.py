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

def loc_facet_concatenation(facet1, facet2):
    """concatenate two facets for filtering LoC API queries"""
    if isinstance(facet1, str) and isinstance(facet2, str):
        return facet1+facet2
    return "error: improper concatenation"