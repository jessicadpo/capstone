"""Module for TagMe views"""
from html.parser import HTMLParser
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import is_valid_path, reverse
from django.http import Http404, HttpResponse, JsonResponse
from .forms import *
from .queries import *


def homepage(request):
    """View for index page (AKA homepage)"""
    page_forms = {"search_form": SearchForm()}
    return render(request, 'homepage.html', {'forms': page_forms})


def about(request):
    """View for About page"""
    page_forms = {"search_form": SearchForm()}
    return render(request, 'about.html', {'forms': page_forms})


def signup_login(request):
    """View for Sign up/Login page"""
    page_forms = {}
    if request.method == 'GET':
        page_forms = {"signup_form": SignUpForm(), "login_form": LoginForm()}

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
            next_url = request.POST.get('referrer')
            parsed_url = urlparse(next_url)
            if parsed_url.netloc and is_valid_path(parsed_url.path):
                return redirect(next_url)
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
            next_url = request.POST.get('referrer')
            parsed_url = urlparse(next_url)
            if parsed_url.netloc and is_valid_path(parsed_url.path):
                return redirect(next_url)
            return redirect("/")
        page_forms = {"signup_form": SignUpForm(), "login_form": login_form}  # If login_form is invalid

    return render(request, 'signup_login.html', {'forms': page_forms})


def logout_view(request):
    """View for Logout Functionality"""
    logout(request)
    return redirect("homepage")


@login_required
def user_profile(request, username):
    """View for a user's "My Profile" page"""
    page_forms = {"search_form": SearchForm(), "equip_form": EquipForm()}
    score_data = {'user_points': -1, 'points_since_last_reward': -1}

    # Redirect user to their own profile page if they try to access someone else's
    if request.user.username != username:
        return redirect(reverse('user_profile', args=[request.user.username]))

    # If POST request for equipping a title
    if request.method == "POST" and ('title_to_equip' in request.POST):
        process_equip_form(request)
        return HttpResponse(status=204)  # NOT a render() so that page doesn't reload

    next_reward = get_next_reward(request.user)
    equipped_title_1, equipped_title_2 = get_equipped_titles(request.user)
    earned_titles = get_earned_rewards(request.user)
    score_data['user_points'] = get_user_total_points(request.user)
    if earned_titles is not None:
        most_recent_reward = max(earned_titles, key=lambda title: title["points_required"])
        score_data["points_since_last_reward"] = score_data['user_points'] - most_recent_reward['points_required']

    return render(request, 'user_profile.html', {
        'forms': page_forms,
        'next_reward': next_reward,
        'equipped_title_1': equipped_title_1,
        'equipped_title_2': equipped_title_2,
        'earned_titles': earned_titles,
        'score_data': score_data
    })


@login_required
def account_settings(request, username):
    """View for a user's "Account Settings" page"""
    # Default page_forms (e.g., if GET request)
    page_forms = {"search_form": SearchForm(),
                  "username_change_form": UsernameChangeForm(request.user),
                  "email_change_form": EmailChangeForm(request.user),
                  "password_change_form": CustomPasswordChangeForm(request.user)}

    # Redirect user to their own Account Settings page if they try to access someone else's
    if request.user.username != username:
        return redirect(reverse('account_settings', args=[request.user.username]))

    # If POST request for changing user's username
    if request.method == 'POST' and ('new_username' in request.POST):
        page_forms['username_change_form'], change_success = process_username_change_form(request)
        # Reload page with updated URL if username was successfully changed
        # else (if failed): Continue to normal render (contains form with the detected form errors)
        if change_success:
            return redirect('account_settings', username=request.user.username)

    elif request.method == 'POST' and ('new_email' in request.POST):
        page_forms['email_change_form'] = process_email_change_form(request)

    elif request.method == 'POST' and ('new_password1' in request.POST):
        page_forms['password_change_form'] = process_password_change_form(request)

    elif request.method == 'POST' and ('delete_account' in request.POST):
        request.user.delete()
        return redirect("/")  # Redirect to homepage (user will be logged out)

    return render(request, 'account_settings.html', {
        'forms': page_forms
    })


@login_required
def pinned_items(request, username):
    """View for a user's "Pinned Items" page"""
    page_forms = {"search_form": SearchForm(),
                  "tags_form": TagsForm(),
                  "equip_form": EquipForm()}  # SortFilterForm added AFTER POST requests are processed
    score_data = {'user_points': -1, 'new_rewards': None}

    # Redirect user to their own Pinned Items page if they try to access someone else's
    if request.user.username != username:
        return redirect(reverse('pinned_items', args=[request.user.username]))

    # If POST request for adding/editing tags on an item
    if request.method == 'POST' and ('tagged_item' in request.POST):
        results_on_search_page = request.session.get('results_on_page', {})  # Set by the first GET request
        item_data = results_on_search_page.get(str(request.POST['tagged_item']))
        score_data = process_tags_form(request, item_data, score_data)

    # If POST request for equipping a title
    elif request.method == "POST" and ('title_to_equip' in request.POST):
        #  Note: Tags already updated in front-end from a previous POST request
        process_equip_form(request)
        return HttpResponse(status=204)  # NOT a render() so that page doesn't reload AGAIN

    # If request is AJAX (i.e., pagination request)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        all_filtered_pinned_items = request.session.get('results_on_page', {})  # Retrieve pinned item list from the session
        current_page = Paginator(list(all_filtered_pinned_items.values()), 15).get_page(request.GET.get('page', 1))
        full_page_html = render_to_string('pinned_items.html',
                                          {'forms': page_forms, 'current_page': current_page},
                                          request)
        return JsonResponse({'html': extract_paginated_html(full_page_html), 'url_name': request.resolver_match.url_name})

    # ----------IF NOT a pagination (AJAX) request----------
    # If all filters are empty/default values --> do NOT show "Clear Sort & Filter(s)" button
    show_clear_filters = True
    if is_default_sort_and_filter(request.GET):
        show_clear_filters = False

    # Create SortFilterForm AFTER any/all POST requests are done so that it uses correct tag counts
    # (i.e., calculated AFTER processing tags form / adding tags to database)
    filtered_pinned_items, filtered_contribs = get_filtered_user_pinned_items(request.user, request.GET)
    user_contribution_types_with_item_counts = get_user_contribution_types_with_item_counts(request.user, filtered_contribs)
    frequent_user_tags_with_item_counts = get_5_most_frequent_user_tags_with_item_counts(request.user, filtered_contribs)

    page_forms['sort_filter_form'] = SortFilterForm(request.GET, user_contribution_types_with_item_counts)

    # If GET request doesn't contain 'page' --> returns page 1 by default
    current_page = Paginator(filtered_pinned_items, 15).get_page(request.GET.get('page', 1))

    # Store ALL filtered pins (NOT just those on current page) in session (if there are any).
    # Storing ALL pins so that pagination can be done without needing to re-filter items every time.
    # Still storing in "results_on_page" session attribute since that's what item_page view needs.
    # Otherwise, links to item pages from the Pinned Items page would not work.
    if filtered_pinned_items is not None:
        request.session['results_on_page'] = {item['item_id']: item for item in filtered_pinned_items}

    return render(request, 'pinned_items.html', {
        'forms': page_forms,
        'current_page': current_page,
        'frequent_user_tags': frequent_user_tags_with_item_counts,
        'show_clear_filters': show_clear_filters,
        'score_data': score_data,  # Need this so can trigger "Congrats!" popup
    })


def search_results(request, requested_page_number):
    """View for Search Results pages"""
    page_forms = {"search_form": SearchForm(), "tags_form": TagsForm(), "equip_form": EquipForm()}
    score_data = {'user_points': -1, 'new_rewards': None}

    # If POST request for adding/editing tags on an item
    if request.method == 'POST' and ('tagged_item' in request.POST):
        results_on_search_page = request.session.get('results_on_page', {})  # Set by the first GET request
        item_data = results_on_search_page.get(str(request.POST['tagged_item']))
        score_data = process_tags_form(request, item_data, score_data)

    # If POST request for equipping a title
    elif request.method == "POST" and ('title_to_equip' in request.POST):
        #  Note: Tags already updated in front-end from a previous POST request
        process_equip_form(request)
        return HttpResponse(status=204)  # NOT a render() so that page doesn't reload AGAIN

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
            item_data['points_earned'] = get_user_points_for_item(request.user, item_data["item_id"])

    # Get lists of synonymous & related tags
    synonymous_tags = get_synonymous_tags(request.GET.get('search_string'))
    related_tags = get_related_tags(request.GET.get('search_string'))

    # Store results in session
    request.session['results_on_page'] = {item['item_id']: item for item in results_on_page}

    return render(request, 'search_results.html', {
        'current_page': results_on_page,
        'pagination': pagination,
        'forms': page_forms,
        'synonymous_tags': synonymous_tags,
        'related_tags': related_tags,
        'score_data': score_data,  # Need this so can trigger "Congrats!" popup
    })


def item_page(request, item_id):
    """View for Item pages"""
    results_from_referrer = request.session.get('results_on_page', {})  # Retrieve item list from the session
    item_data = results_from_referrer.get(str(item_id))  # Get the specific item's LOC API data using the item ID
    score_data = {'user_points': -1, 'new_rewards': None}

    # If POST request for adding/editing tags on an item
    if request.method == 'POST' and ('tagged_item' in request.POST):
        score_data = process_tags_form(request, item_data, score_data)

    # If POST request for equipping a title
    elif request.method == "POST" and ('title_to_equip' in request.POST):
        # Note: Page needs to reload if equipping a title from an item page in case user has comment
        # for whom the equipped_titles need to be updated
        process_equip_form(request)

    # If POST request for reporting a tag
    elif request.method == 'POST' and ('reported_tag' in request.POST):
        process_report_form(request, item_id)

    # If POST request for adding a comment
    elif request.method == 'POST' and ('comment' in request.POST):
        process_comment_form(request, item_data)

    page_forms = {"search_form": SearchForm(),
                  "tags_form": TagsForm(),
                  "comment_form": CommentForm(),
                  "report_form": ReportForm(),
                  "equip_form": EquipForm()}
    item_data['tags'] = get_all_tags_for_item(item_id)

    # Ensure user's own comment is always the first comment on page 1
    all_item_comments = get_all_comments_for_item(item_id, request.user)

    # If GET request doesn't contain 'page' --> returns page 1 by default
    current_page = Paginator(all_item_comments, 15).get_page(request.GET.get('page', 1))

    if request.user.is_authenticated:
        user_public_tags, user_private_tags = get_user_tags_for_item(request.user, item_id)
        item_data['user_public_tags'] = user_public_tags
        item_data['user_private_tags'] = user_private_tags
        item_data['user_comment'] = get_user_comment_for_item(request.user, item_id)
        item_data['is_pinned'] = get_is_item_pinned(request.user, item_id)
        item_data['points_earned'] = get_user_points_for_item(request.user, item_data["item_id"])

    if not item_data:
        raise Http404("Item not found")

    # If request is AJAX (i.e., pagination request)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        full_page_html = render_to_string('item_page.html',
                                          {'item': item_data, 'forms': page_forms, 'current_page': current_page},
                                          request)
        return JsonResponse({'html': extract_paginated_html(full_page_html), 'url_name': request.resolver_match.url_name})

    return render(request, 'item_page.html', {
        'item': item_data,
        'forms': page_forms,
        'current_page': current_page,
        'score_data': score_data,  # Need this so can trigger "Congrats!" popup
    })










def process_tags_form(request, item_data, score_data):
    """Function for processing "Add Tags" form"""
    tags_form = TagsForm(request.POST)
    if tags_form.is_valid():  # cleans form inputs
        prev_score = get_user_total_points(request.user)
        set_item(item_data)
        set_user_tags_for_item(request.user, tags_form.cleaned_data)
        score_data['user_points'] = get_user_total_points(request.user)
        score_data['new_rewards'] = get_new_rewards(prev_score, score_data['user_points'])
    return score_data


def process_equip_form(request):
    """Function for processing \"Equip Title\" form"""
    equip_form = EquipForm(request.POST)
    if equip_form.is_valid():
        set_equipped_title(request.user, equip_form)


def process_report_form(request, item_id):
    """Function for processing "Report Tag" form"""
    report_form = ReportForm(request.POST)
    if report_form.is_valid():
        create_tag_report(request.user, item_id, report_form.cleaned_data)


def process_comment_form(request, item_data):
    """Function for processing "Add Comment" form"""
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        if comment_form.cleaned_data.get("request_delete_comment"):
            delete_user_comment_for_item(request.user, item_data['item_id'])
        else:
            set_item(item_data)
            set_user_comment_for_item(request.user, item_data['item_id'], comment_form.cleaned_data)


def process_username_change_form(request):
    """
    Function for processing "Change Username" form
    If successfully changed the username --> returns a new username_change_form && True
    If failed to change username --> returns the username_change_form with the errors found && False
    """
    username_change_form = UsernameChangeForm(data=request.POST, user=request.user)
    if username_change_form.is_valid():
        username_change_form.save()
        return UsernameChangeForm(request.user), True
    return username_change_form, False  # If form is invalid


def process_email_change_form(request):
    """Function for processing "Change Email" form"""
    email_change_form = EmailChangeForm(data=request.POST, user=request.user)
    if email_change_form.is_valid():
        email_change_form.save()
        return EmailChangeForm(request.user)
    return email_change_form  # If form is invalid


def process_password_change_form(request):
    """Function for processing "Change Password" form"""
    password_change_form = CustomPasswordChangeForm(data=request.POST, user=request.user)
    if password_change_form.is_valid():
        password_change_form.save()
        return CustomPasswordChangeForm(request.user)
    return password_change_form  # If form is invalid
