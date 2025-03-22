"""Module for TagMe views"""
from urllib.parse import urlparse

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
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
    page_forms = {"signup_form": SignUpForm(),
                  "login_form": LoginForm()}

    if request.method == "POST":
        page_forms, success = process_post_form(request, page_forms=page_forms)
        if success:
            next_url = request.POST.get('referrer')
            parsed_url = urlparse(next_url)
            if parsed_url.netloc and is_valid_path(parsed_url.path):  # Ensure next_url is safe or default to home page
                return redirect(next_url)  # Redirect user to the page they were previously on
            return redirect("/")
    return render(request, 'signup_login.html', {'forms': page_forms})


def logout_view(request):
    """View for Logout Functionality"""
    logout(request)
    return redirect("homepage")


@login_required(login_url="/signup-login")  # TODO: TEST if works
def user_profile(request, username):
    """View for a user's "My Profile" page"""
    page_forms = {"search_form": SearchForm(),
                  "equip_form": EquipForm()}
    score_data = {'user_points': -1, 'points_since_last_reward': -1}

    if request.user.username != username:  # Redirect user to their own profile page if they try to access someone else's
        return redirect(reverse('user_profile', args=[request.user.username]))

    if request.method == "POST":
        form_result = process_post_form(request)  # Only POST form on User Profile == EquipForm
        if form_result is True:  # If processed EquipForm && new title equipped successfully
            return HttpResponse(status=204)  # NOT a render() so that page doesn't reload AGAIN

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


@login_required(login_url="/signup-login")
def account_settings(request, username):
    """View for a user's "Account Settings" page"""
    # Default page_forms (e.g., if GET request)
    page_forms = {"search_form": SearchForm(),
                  "username_change_form": UsernameChangeForm(request.user),
                  "email_change_form": EmailChangeForm(request.user),
                  "password_change_form": CustomPasswordChangeForm(request.user),
                  "delete_account_form": DeleteAccountForm()}

    if request.user.username != username:  # Redirect user to their own profile page if they try to access someone else's
        return redirect(reverse('account_settings', args=[request.user.username]))

    if request.method == "POST":
        form_result = process_post_form(request, page_forms=page_forms)
        if form_result == "DeleteAccountForm":
            request.user.delete()
            return redirect("/")  # Redirect to homepage (user will be logged out)

        if "new_username" in request.POST and form_result[1]:  # If processed a UsernameChangeForm
            return redirect('account_settings', username=request.user.username)
            # Reload page with updated URL if username was successfully changed (i.e., form_result[1] == True)
            # else (if failed): Continue to normal render (contains form with the detected form errors)

        page_forms = form_result[0]

    return render(request, 'account_settings.html', {'forms': page_forms})


@login_required(login_url="/signup-login")
def pinned_items(request, username):
    """View for a user's "Pinned Items" page"""
    page_forms = {"search_form": SearchForm(),
                  "tags_form": TagsForm(),
                  "equip_form": EquipForm()}  # SortFilterForm added AFTER POST requests are processed
    score_data = {'user_points': -1, 'new_rewards': None}

    if request.user.username != username:  # Redirect user to their own profile page if they try to access someone else's
        return redirect(reverse('pinned_items', args=[request.user.username]))

    if request.method == "POST":
        item_data = get_item_from_session(request)
        form_result = process_post_form(request, item_data)
        if isinstance(form_result, dict):
            score_data = form_result
        elif form_result is True:  # If processed EquipForm && new title equipped successfully
            return HttpResponse(status=204)  # NOT a render() so that page doesn't reload AGAIN

    # ----------If AJAX request (i.e., page already loaded)----------
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        filtered_pinned_items = list(request.session.get('results_from_referrer').values())
        current_page = paginate(request, filtered_pinned_items, "pinned_items.html", page_forms)
        return JsonResponse({'html': current_page, 'url_name': request.resolver_match.url_name})

    # ----------IF NOT AJAX request (i.e., page loading for the first time)----------
    # If all filters are empty/default values --> do NOT show "Clear Sort & Filter(s)" button
    # show_clear_filters == opposite of is_default_sort_and_filter()
    show_clear_filters = not is_default_sort_and_filter(request.GET)

    filtered_pinned_items, filtered_contribs = get_filtered_user_pinned_items(request.user, request.GET)
    user_contribution_types_with_item_counts = get_user_contribution_types_with_item_counts(request.user, filtered_contribs)
    frequent_user_tags_with_item_counts = get_5_most_frequent_user_tags_with_item_counts(request.user, filtered_contribs)

    # Create SortFilterForm AFTER any/all POST requests are done so that it uses correct tag counts
    # (i.e., calculated AFTER processing tags form / adding tags to database)
    page_forms['sort_filter_form'] = SortFilterForm(request.GET, user_contribution_types_with_item_counts)

    # Store ALL filtered pins (NOT just those on current page) in session (if there are any).
    # Storing ALL pins so that pagination can be done without needing to re-filter items every time.
    # Still storing in "results_from_referrer" session attribute since that's what item_page view needs.
    # Otherwise, links to item pages from the Pinned Items page would not work.
    if filtered_pinned_items is not None:
        request.session['results_from_referrer'] = {item['item_id']: item for item in filtered_pinned_items}

    current_page = paginate(request, filtered_pinned_items, "pinned_items.html", page_forms)

    return render(request, 'pinned_items.html', {
        'forms': page_forms,
        'current_page': current_page,
        'frequent_user_tags': frequent_user_tags_with_item_counts,
        'show_clear_filters': show_clear_filters,
        'score_data': score_data,  # Need this so can trigger "Congrats!" popup
    })


def search_results(request, requested_page_number):
    """View for Search Results pages"""
    page_forms = {"search_form": SearchForm(),
                  "tags_form": TagsForm(),
                  "equip_form": EquipForm()}
    score_data = {'user_points': -1, 'new_rewards': None}

    if request.method == "POST":
        item_data = get_item_from_session(request)
        form_result = process_post_form(request, item_data)
        if isinstance(form_result, dict):
            score_data = form_result
        elif form_result is True:  # If processed EquipForm && new title equipped successfully
            return HttpResponse(status=204)  # NOT a render() so that page doesn't reload AGAIN

    # TODO: Code for parsing AND/OR/NOT/*/? --> Investigate pyparsing & Shunting Yard algorithm

    search_string = request.GET.get('search_string')
    results_on_page = []
    pagination = None
    match request.GET.get('search_type'):
        case "Keyword":
            results_on_page, pagination = query_loc_keyword(search_string, requested_page_number)
            clean_search_string = remove_globally_banned_tags_from_tag_search(search_string)  # pylint: disable=unused-variable
            # Disable pylint ignore once finish this
            # TODO: Need to also search our UserContribution model
        case "Tag":
            clean_search_string = remove_globally_banned_tags_from_tag_search(search_string)  # pylint: disable=unused-variable
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
    request.session['results_from_referrer'] = {item['item_id']: item for item in results_on_page}

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
    page_forms = {"search_form": SearchForm(),
                  "tags_form": TagsForm(),
                  "comment_form": CommentForm(),
                  "report_form": ReportForm(),
                  "equip_form": EquipForm()}
    score_data = {'user_points': -1, 'new_rewards': None}
    item_data = get_item_from_session(request, item_id)  # Get the specific item's LOC API data using the item ID
    if item_data is None:  # If accessing item page by directly pasting a URL, for example
        item_data = query_loc_single_item(item_id)

    if request.method == "POST":
        form_result = process_post_form(request, item_data)
        if isinstance(form_result, dict):
            score_data = form_result
        # W.R.T. PROCESSING EQUIP FORM --> Page needs to reload if equipping a title from
        # an item page in case user has comment for whom the equipped_titles need to be updated

    item_data['tags'] = get_all_tags_for_item(item_id)
    all_item_comments = get_all_comments_for_item(item_id, request.user)

    if request.user.is_authenticated:
        user_public_tags, user_private_tags = get_user_tags_for_item(request.user, item_id)
        item_data['user_public_tags'] = user_public_tags
        item_data['user_private_tags'] = user_private_tags
        item_data['user_comment'] = get_user_comment_for_item(request.user, item_id)
        item_data['is_pinned'] = get_is_item_pinned(request.user, item_id)
        item_data['points_earned'] = get_user_points_for_item(request.user, item_data["item_id"])

    if not item_data:
        raise Http404("Item not found")

    current_page = paginate(request, all_item_comments, "item_page.html", page_forms, item_data)

    # ----------If AJAX request (i.e., page already loaded)----------
    if isinstance(current_page, str):
        return JsonResponse({'html': current_page, 'url_name': request.resolver_match.url_name})

    # ----------IF NOT AJAX request (i.e., page loading for the first time)----------
    return render(request, 'item_page.html', {
        'item': item_data,
        'forms': page_forms,
        'current_page': current_page,
        'score_data': score_data,  # Need this so can trigger "Congrats!" popup
    })


########################################################################################################################
# FORM PROCESSING

def process_post_form(request, item_data=None, page_forms=None):
    """Function for efficient calling of the appropriate form-processing function"""
    if request.method != "POST":
        raise ValueError("process_post_form() can only be called if the request.method is POST.")

    match(request.POST["form_id"]):
        case "SignUpForm":
            page_forms['signup_form'], success = process_signup_form(request)
            return page_forms, success  # Returns a (dict, bool) tuple
        case "LoginForm":
            page_forms['login_form'], success = process_login_form(request)
            return page_forms, success  # Returns a (dict, bool) tuple

        case "TagsForm":
            return process_tags_form(request, item_data)  # Returns a dict (score_data) (or None if invalid form)
        case "EquipForm":
            return process_equip_form(request)  # Returns True or False
        case "ReportForm":
            return process_report_form(request, item_data['item_id'])  # Returns nothing (None)
        case "CommentForm":
            return process_comment_form(request, item_data)  # Returns nothing (None)

        case "UsernameChangeForm":
            page_forms['username_change_form'], success = process_username_change_form(request)
            return page_forms, success  # Returns a (dict, bool) tuple
        case "EmailChangeForm":
            page_forms['email_change_form'], success = process_email_change_form(request)
            return page_forms, success   # Returns a (dict, bool) tuple
        case "CustomPasswordChangeForm":
            page_forms['password_change_form'], success = process_password_change_form(request)
            return page_forms, success   # Returns a (dict, bool) tuple
        case "DeleteAccountForm":
            # Form doesn't require processing
            return "DeleteAccountForm"  # Returns a string (to differentiate from other form return types)

        case _:
            return None


def process_signup_form(request):
    """
    Function for processing "Sign Up" form
    If successfully created user account --> returns a new SignUpForm && True
    If failed --> returns the SignUpForm with the errors found && False
    """
    # NOTE: USERNAMES MUST BE UNIQUE
    signup_form = SignUpForm(request.POST)
    if signup_form.is_valid():
        signup_form.save()
        username = signup_form.cleaned_data.get('username').lower()
        password = signup_form.cleaned_data.get('password1')
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return SignUpForm(), True
    return signup_form, False


def process_login_form(request):
    """
    Function for processing "Login" form
    If successfully logged in --> returns a new LoginForm && True
    If failed --> returns the LoginForm with the errors found && False
    """
    login_form = LoginForm(request.POST)
    if login_form.is_valid():
        username = login_form.cleaned_data.get('username').lower()
        password = login_form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return LoginForm(), True
    return login_form, False


def process_tags_form(request, item_data):
    """Function for processing "Add Tags" form"""
    tags_form = TagsForm(request.POST)
    if tags_form.is_valid():  # cleans form inputs
        prev_score = get_user_total_points(request.user)
        set_item(item_data)
        set_user_tags_for_item(request.user, tags_form.cleaned_data)
        user_total_points = get_user_total_points(request.user)
        score_data = {'user_points': user_total_points,
                      'new_rewards': get_new_rewards(prev_score, user_total_points)}
        return score_data
    return None


def process_equip_form(request):
    """
    Function for processing "Equip Title" form.
    Returns True if new title equipped successfully. False if not.
    """
    # NOTE: If form triggered by new_reward_modal (i.e., user added new tags)
    # --> tags already updated in front-end from a previous POST request
    equip_form = EquipForm(request.POST)
    if equip_form.is_valid():
        set_equipped_title(request.user, equip_form)
        return True
    return False


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
    If successfully changed the username --> returns a new UsernameChangeForm && True
    If failed to change username --> returns the UsernameChangeForm with the errors found && False
    """
    username_change_form = UsernameChangeForm(data=request.POST, user=request.user)
    if username_change_form.is_valid():
        username_change_form.save()
        return UsernameChangeForm(request.user), True
    return username_change_form, False


def process_email_change_form(request):
    """
    Function for processing "Change Email" form
    If successfully changed the email --> returns a new EmailChangeForm && True
    If failed to change email --> returns the EmailChangeForm with the errors found && False
    """
    email_change_form = EmailChangeForm(data=request.POST, user=request.user)
    if email_change_form.is_valid():
        email_change_form.save()
        return EmailChangeForm(request.user), True
    return email_change_form, False


def process_password_change_form(request):
    """
    Function for processing "Change Password" form
    If successfully changed the password --> returns a new CustomPasswordChangeForm && True
    If failed to change password --> returns the CustomPasswordChangeForm with the errors found && False
    """
    password_change_form = CustomPasswordChangeForm(data=request.POST, user=request.user)
    if password_change_form.is_valid():
        password_change_form.save()
        update_session_auth_hash(request, request.user)  # Prevent auto-logout
        return CustomPasswordChangeForm(request.user), True
    return password_change_form, False
