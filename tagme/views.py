"""Module for TagMe views"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import is_valid_path
from django.http import Http404
from django.core.paginator import Paginator
from urllib.parse import urlparse, quote
from .forms import *
from .api_queries import *


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
    page_forms = {"search_form": SearchForm()}

    search_type = request.GET.get('search_type')
    search_string = request.GET.get('search_string')

    # TODO: Insert search system code here
    results_on_page = []  # Replace with API calls / Django query
    pagination: None

    # Pylint doesn't know match (because match is new and pylint is old)
    match search_type:  # pylint: disable=syntax-error
        case "Keyword":
            results_on_page, pagination = query_loc_keyword(search_string, requested_page_number)
            # TODO: Need to also search our UserContribution model
        case "Tag":
            print("placeholder code")
        case "Title":
            print("placeholder code")
        case "Author":
            print("placeholder code")
        case "Subject":
            print("placeholder code")
        case _:
            raise Http404("Invalid search type")

    # Store results in session
    request.session['results_on_page'] = {item['item_id']: item for item in results_on_page}

    return render(request, 'search_results.html', {
        'current_page': results_on_page,
        'pagination': pagination,
        'forms': page_forms})


def item_page(request, item_id):
    """View for Item pages"""
    page_forms = {"search_form": SearchForm(), "report_form": ReportForm()}
    results_on_search_page = request.session.get('results_on_page', {})  # Retrieve search results from the session
    item = results_on_search_page.get(str(item_id))  # Get the specific item using the item ID
    if not item:
        raise Http404("Item not found")
    return render(request, 'item_page.html', {'item': item, 'forms': page_forms})



