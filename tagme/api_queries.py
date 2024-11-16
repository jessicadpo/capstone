"""
Module for querying Library of Congress & Datamuse APIs

RATE LIMIT FOR LIBRARY OF CONGRESS API: 20 queries per 10 seconds && 80 queries per 1 minute

"""
import requests
from urllib.parse import quote
from .helper_functions import *


def query_loc_keyword(search_string, requested_page_number):
    params = {
        "q": search_string,  # Default parameters set in _query_loc_api() function
    }
    return _query_loc_api(params, requested_page_number)


def query_loc_title(search_string, requested_page_number):
    print("TODO (placeholder code)")


def query_loc_author(search_string, requested_page_number):
    print("TODO (placeholder code)")


def query_loc_subject(search_string, requested_page_number):
    print("TODO (placeholder code)")


def _query_loc_api(params, requested_page_number):
    params["fa"] = "partof:general collections"
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
            id_url = item.get('url')
            title = decode_unicode(strip_punctuation(item.get('title', 'No title available')))
            publication_date = decode_unicode(item.get('date', 'No publication date available'))
            description = decode_unicode(item.get('description', 'No description available'))

            authors = item.get('contributor', ['No authors listed'])
            for i in range(len(authors)):
                authors[i] = decode_unicode(to_firstname_lastname(authors[i]))

            covers = item.get('image_url', None)
            cover = covers[0] if covers else None

            results_on_page.append({
                'id': id_url,
                'title': to_title_case(title),
                'authors': to_title_case('; '.join(authors)),  # Combine authors into a single string
                'publication_date': publication_date,
                'description': description,
                'cover': cover
            })

        return results_on_page, data.get("pagination")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return [], 0


__all__ = [name for name in globals()]
__all__.remove('_query_loc_api')  # Remove _query_loc_api from exportable functions (i.e., make function private)
