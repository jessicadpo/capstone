"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# pragma pylint: disable=undefined-variable
from django.urls import path
from .views import *

urlpatterns = [
    # Cannot start URLs with <str:username> because of conflicts if username is "admin"
    path('', homepage, name="homepage"),
    path('signup-login', signup_login),
    path('profile/<str:username>', user_profile, name="user_profile"),
    path('pinned-items/<str:username>', pinned_items, name="pinned_items"),
    path('account-settings/<str:username>', account_settings, name="account_settings"),
    path('logout', logout_view),
    path('search/<str:requested_page_number>/', search_results, name="search_results"),
    path('item/<str:item_id>/', item_page, name="item_page"),
    path('about', about),
]
