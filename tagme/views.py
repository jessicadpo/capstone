"""Module for TagMe views"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import is_valid_path
from urllib.parse import urlparse
from .forms import SignUpForm, LoginForm

def homepage(request):
    """View for index page (AKA homepage)"""
    #if request.method == 'POST':
        #advanced_search()
    return render(request, 'homepage.html')


def signup_login(request):
    """View for Sign up/Login page"""
    forms = {}
    if request.method != 'POST':
        forms = {"signup_form": SignUpForm(), "login_form": LoginForm()}  # If request.method == 'GET'

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
                return redirect(next_url)
            return redirect("/")
        forms = {"signup_form": signup_form, "login_form": LoginForm()}  # If login_form is invalid

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
                return redirect(next_url)
            return redirect("/")
        forms = {"signup_form": SignUpForm(), "login_form": login_form}  # If login_form is invalid

    return render(request, 'signup_login.html', {'forms': forms})


def logout_view(request):
    """View for Logout Functionality"""
    logout(request)
    return redirect("homepage")


def about(request):
    """View for About page"""
    return render(request, 'about.html')