"""Module for TagMe views"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LoginForm

def homepage(request):
    """View for index page (AKA homepage)"""
    #if request.method == 'POST':
        #advanced_search()
    return render(request, 'homepage.html')


def signup_login(request):
    """View for Sign up/Login page"""
    # NOTE: USERNAMES MUST BE UNIQUE
    if request.method == 'POST':
        if 'signup-submit' in request.POST:
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(request, username=username, password=password)
                login(request, user)
                return redirect("user-profile-page", username=username)
            forms = {"signup_form": form, "login_form": LoginForm()}
            return render(request, 'signup_login.html', {'forms': forms})

        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect("user-profile-page", username=username)
        forms = {"signup_form": SignUpForm(), "login_form": form}
        return render(request, 'signup_login.html', {'forms': forms})
    forms = {"signup_form": SignUpForm(), "login_form": LoginForm()}
    return render(request, 'signup_login.html', {'forms': forms})


def logout_view(request):
    """View for Logout Functionality"""
    logout(request)
    return redirect("homepage")


def about(request):
    """View for About page"""
    return render(request, 'about.html')


def sitemap(request):
    """View for Sitemap page"""
    return render(request, 'sitemap.html')
