"""Module for TagMe views"""
from urllib.parse import urlparse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import is_valid_path, reverse
from django.http import Http404, HttpResponse
from .forms import *
from .queries import *


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


def logout_view(request):
    """View for Logout Functionality"""
    logout(request)
    return redirect("homepage")


def about(request):
    """View for About page"""
    return render(request, 'about.html')


def search_results(request, requested_page_number):
    """View for Search Results pages"""
    page_forms = {"search_form": SearchForm(), "tags_form": TagsForm(), "equip_form": EquipForm()}
    score_data = {'user_points': -1, 'new_rewards': None}

    # If POST request for adding/editing tags on an item
    if request.method == 'POST' and ('tagged_item' in request.POST):
        score_data = process_tags_form(request, score_data)

    # If POST request for equipping a title
    elif request.method == "POST" and ('title_to_equip' in request.POST):
        #  Note: Page needs to reload if equipping a title from a search_results page (to update added tags, etc.)
        process_equip_form(request)

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

    # Store results in session # TODO: Double-check I did this for the "Return to Search Results" button in item page
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
    score_data = {'user_points': -1, 'new_rewards': None}

    # If POST request for adding/editing tags on an item
    if request.method == 'POST' and ('tagged_item' in request.POST):
        score_data = process_tags_form(request, score_data)

    # If POST request for equipping a title
    elif request.method == "POST" and ('title_to_equip' in request.POST):
        #  Note: Page needs to reload if equipping a title from a search_results page (to update added tags, etc.)
        process_equip_form(request)

    # If POST request for reporting a tag
    elif request.method == 'POST' and ('reported_tag' in request.POST):
        process_report_form(request, item_id)

    # If POST request for adding a comment
    elif request.method == 'POST' and ('comment' in request.POST):
        process_comment_form(request, item_id)

    page_forms = {"search_form": SearchForm(), "tags_form": TagsForm(), "report_form": ReportForm(), "equip_form": EquipForm()}
    results_on_search_page = request.session.get('results_on_page', {})  # Retrieve search results from the session
    item_data = results_on_search_page.get(str(item_id))  # Get the specific item using the item ID
    item_data['tags'] = get_all_tags_for_item(item_id)

    if request.user.is_authenticated:
        user_public_tags, user_private_tags = get_user_tags_for_item(request.user, item_id)
        item_data['user_public_tags'] = user_public_tags
        item_data['user_private_tags'] = user_private_tags
        item_data['is_pinned'] = get_is_item_pinned(request.user, item_id)
        item_data['points_earned'] = get_user_points_for_item(request.user, item_data["item_id"])

    if not item_data:
        raise Http404("Item not found")

    return render(request, 'item_page.html', {
        'item': item_data,
        'forms': page_forms,
        'score_data': score_data,  # Need this so can trigger "Congrats!" popup
    })


def process_tags_form(request, score_data):
    """Function for processing "Add Tags" form"""
    tags_form = TagsForm(request.POST)
    if tags_form.is_valid():  # cleans form inputs
        prev_score = get_user_total_points(request.user)
        set_user_tags_for_item(request.user, tags_form.cleaned_data)
        score_data['user_points'] = get_user_total_points(request.user)
        score_data['new_rewards'] = get_new_rewards(prev_score, score_data['user_points'])
    return score_data


def process_equip_form(request):
    """Function for processing \"Equip Title\" form"""
    equip_form = EquipForm(request.POST)
    if equip_form.is_valid():
        title_to_equip = equip_form.cleaned_data.get('title_to_equip')
        slot = equip_form.cleaned_data.get('slot')  # Can be '1' or '2'

        if not title_to_equip or slot not in ['1', '2']:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        user_profile = get_object_or_404(UserProfile, user=request.user)
        reward = get_object_or_404(Reward, title=title_to_equip)

        # Check if the user has enough points to equip this title
        if reward.points_required > user_profile.points:
            return JsonResponse({'error': 'Insufficient points to equip this title'}, status=403)

        # Equip the title in the specified slot
        if slot == '1':
            user_profile.equipped_title_1 = reward
        elif slot == '2':
            user_profile.equipped_title_2 = reward

        user_profile.save()
        return JsonResponse({'success': f'Title \"{title_to_equip}\" equipped in slot {slot}.'})

    return JsonResponse({'error': 'Invalid form data'}, status=400)


def process_report_form(request, item_id):
    """Function for processing "Report Tag" form"""
    report_form = ReportForm(request.POST)
    if report_form.is_valid():
        create_tag_report(request.user, item_id, report_form.cleaned_data)


def process_comment_form(request, item_id):
    """Function for processing "Add Comment" form"""
    # TODO
    print(f'placeholder code{request, item_id}')




def unequip_title(request):
    """Function for unequipping a title."""
    if request.method == 'POST':
        slot = request.POST.get('slot')  # Can be '1' or '2'

        if slot not in ['1', '2']:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        user_profile = get_object_or_404(UserProfile, user=request.user)

        # Unequip the title in the specified slot
        if slot == '1':
            user_profile.equipped_title_1 = None
        elif slot == '2':
            user_profile.equipped_title_2 = None

        user_profile.save()
        return JsonResponse({'success': f'Title unequipped from slot {slot}.'})

