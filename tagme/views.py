"""Module for TagMe views"""
from urllib.parse import urlparse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import is_valid_path
from django.http import Http404
from .forms import *
from .queries import *
from .models import UserProfile


def homepage(request):
    """View for index page (AKA homepage)"""
    page_forms = {"search_form": SearchForm()}
    return render(request, 'homepage.html', {'forms': page_forms})


def signup_login(request):
    """View for Sign up/Login page"""
    page_forms = {}
    if request.method != 'POST':
        page_forms = {"signup_form": SignUpForm(), "login_form": LoginForm()}  # If request.method == 'GET'

    # NOTE: USERNAMES MUST BE UNIQUE
    elif request.method == 'POST' and ('signup-submit' in request.POST):
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            signup_form.save()
            username = signup_form.cleaned_data.get('username')
            password = signup_form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            extended_user = UserProfile(user=user)
            extended_user.save()  # Create UserProfile at the same time as user
            login(request, user)

            # Ensure next_url is safe or default to home page
            next_url = request.POST.get('next', request.GET.get('next', '/'))
            parsed_url = urlparse(next_url)
            if not parsed_url.netloc and is_valid_path(next_url):
                return redirect(next_url)  # TODO: This isn't working
            return redirect("/")
        page_forms = {"signup_form": signup_form, "login_form": LoginForm()}  # If login_form is invalid

    elif request.method == 'POST' and ('login-submit' in request.POST):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            login(request, user)

            # Ensure next_url is safe or default to home page
            next_url = request.POST.get('next', request.GET.get('next', '/'))
            parsed_url = urlparse(next_url)
            if not parsed_url.netloc and is_valid_path(next_url):
                return redirect(next_url)  # TODO: This isn't working
            return redirect("/")
        page_forms = {"signup_form": SignUpForm(), "login_form": login_form}  # If login_form is invalid

    return render(request, 'signup_login.html', {'forms': page_forms})


def logout_view(request):
    """View for Logout Functionality"""
    logout(request)
    return redirect("homepage")


def about(request):
    """View for About page"""
    return render(request, 'about.html')


def search_results(request, requested_page_number):
    """View for Search Results pages"""
    page_forms = {"search_form": SearchForm(), "tags_form": TagsForm()}

    # If POST request for adding/editing tags on an item
    if request.method == 'POST' and ('tagged_item' in request.POST):
        tags_form = TagsForm(request.POST)
        if tags_form.is_valid():  # cleans form inputs
            set_user_tags_for_item(request.user, tags_form.cleaned_data)

    # TODO: Code for parsing AND/OR/NOT/*/? --> Investigate pyparsing & Shunting Yard algorithm

    search_string = request.GET.get('search_string')
    results_on_page = []
    pagination: None
    match request.GET.get('search_type'):
        case "Keyword":
            results_on_page, pagination = query_loc_keyword(search_string, requested_page_number)
            # TODO: Need to also search our UserContribution model
        case "Tag":
            print("placeholder code")  # Replace with Django queries
        case "Title":
            print("placeholder code")  # Replace with API call
        case "Author":
            print("placeholder code")  # Replace with API call
        case "Subject":
            print("placeholder code")  # Replace with API call
        case _:
            raise Http404("Invalid search type")

    # Add "is_pinned" to every item in results_on_page
    # Get user's tags for each pinned item in current results
    if request.user.is_authenticated:
        for item_data in results_on_page:
            user_public_tags, user_private_tags = get_user_tags_for_item(request.user, item_data["item_id"])
            item_data['user_public_tags'] = user_public_tags
            item_data['user_private_tags'] = user_private_tags
            item_data['is_pinned'] = get_is_item_pinned(request.user, item_data["item_id"])

    # Get lists of synonymous & related tags
    synonymous_tags = get_synonymous_tags(request.GET.get('search_string'))
    related_tags = get_related_tags(request.GET.get('search_string'))

    # Store results in session # TODO: Double-check I did this for the "Return to Search Results" button in item page
    request.session['results_on_page'] = {item['item_id']: item for item in results_on_page}

    return render(request, 'search_results.html', {
        'current_page': results_on_page,
        'pagination': pagination,
        'forms': page_forms,
        'synonymous_tags': synonymous_tags,
        'related_tags': related_tags,
    })


def item_page(request, item_id):
    """View for Item pages"""
    # If POST request for adding/editing tags on an item
    if request.method == 'POST' and ('tagged_item' in request.POST):
        tags_form = TagsForm(request.POST)
        if tags_form.is_valid():  # cleans form inputs
            set_user_tags_for_item(request.user, tags_form.cleaned_data)

    # If POST request for reporting a tag
    elif request.method == 'POST' and ('reported_tag' in request.POST):
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            create_tag_report(request.user, item_id, report_form.cleaned_data)

    # If POST request for adding a comment
    elif request.method == 'POST' and ('comment' in request.POST):
        print('adding/editing a comment')

    page_forms = {"search_form": SearchForm(), "tags_form": TagsForm(), "report_form": ReportForm()}
    results_on_search_page = request.session.get('results_on_page', {})  # Retrieve search results from the session
    item_data = results_on_search_page.get(str(item_id))  # Get the specific item using the item ID
    item_data['tags'] = get_all_tags_for_item(item_id)

    if request.user.is_authenticated:
        user_public_tags, user_private_tags = get_user_tags_for_item(request.user, item_id)
        item_data['user_public_tags'] = user_public_tags
        item_data['user_private_tags'] = user_private_tags
        item_data['is_pinned'] = get_is_item_pinned(request.user, item_id)

    if not item_data:
        raise Http404("Item not found")
    return render(request, 'item_page.html', {'item': item_data, 'forms': page_forms})
