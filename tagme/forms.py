""""Module containing forms for the LiteReview"""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import connection
from .models import Reward
from .constants import *


########################################################################################################################
# GET-method Forms (NOTE: GET-method forms don't need form_ids (form ids get included in URL otherwise))

class SearchForm(forms.Form):
    """ Form for search bar """
    search_type = forms.ChoiceField(label=False, choices=SEARCH_TYPES, required=True, widget=forms.Select(
        attrs={'id': 'search-type-select'}))
    search_string = forms.CharField(label=False, min_length=1, max_length=999, widget=forms.TextInput(
        attrs={'id': 'search-input', 'placeholder': 'Search', 'label': 'Search',
               'title': 'Use "-" before a search term to exclude items from your search (e.g. "-vampires" in a tag search '
                        'is equivalent to NOT(vampires) and will exclude all items with the "vampires" tag).\n\n'
                        '"AND" relationships are implied between all space-separated search terms (e.g., "mount everest" '
                        'in a tag search will only return items with both "mount" and "everest" in their tags).'}))
    page = forms.IntegerField(widget=forms.HiddenInput(), initial=1)  # New searches will always request page 1


class SortFilterForm(forms.Form):
    """
    Form for sorting & filtering pinned items in the Pinned Items page.
    NOTE: Labels for filter fields are set in __init__
    """
    sort_order = forms.ChoiceField(label=False, choices=SORT_OPTIONS, initial="pindate_no", required=True,
                                   widget=forms.Select(attrs={'id': 'sort-order-select'}))
    public_tags = forms.ChoiceField(label=False, choices=FILTER_STATES, initial=None, required=True,
                                    widget=forms.Select(attrs={'id': 'public-tags-filter'}))
    private_tags = forms.ChoiceField(label=False, choices=FILTER_STATES, initial=None, required=True,
                                     widget=forms.Select(attrs={'id': 'private-tags-filter'}))
    comments = forms.ChoiceField(label=False, choices=FILTER_STATES, initial=None, required=True,
                                 widget=forms.Select(attrs={'id': 'comments-filter'}))

    # HIDDEN FROM USERS
    include_tags = forms.CharField(label=False, required=False, widget=forms.Textarea(attrs={'id': 'include-tags-textarea'}))
    exclude_tags = forms.CharField(label=False, required=False, widget=forms.Textarea(attrs={'id': 'exclude-tags-textarea'}))

    def __init__(self, get_request, contribution_filter_counts):
        super().__init__()

        # Set form labels
        self.fields['public_tags'].label = f"Public Tags ({str(contribution_filter_counts[0])})"
        self.fields['private_tags'].label = f"Private Tags ({str(contribution_filter_counts[1])})"
        self.fields['comments'].label = f"Comments ({str(contribution_filter_counts[2])})"

        # Remove colon appended to the end of labels by Django, for all fields
        for field in self.fields.items():
            field[1].label_suffix = ''

        # Set form initial values
        if len(get_request) > 0:
            # Retrieve all query parameters that aren't -1 (i.e., that are either Include (1) or Exclude (0))
            user_selections = {key: value for key, value in get_request.items() if value != '-1'}
            self.fields['sort_order'].initial = user_selections['sort_order']
            for key in user_selections.keys():
                if key in self.fields:
                    self.fields[key].initial = user_selections[key]


########################################################################################################################
# POST-method Forms

class CommentForm(forms.Form):
    """ Form for adding/editing/deleting a comment """
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(attrs={'value': 'CommentForm'}))
    request_delete_comment = forms.BooleanField(label=False, required=False, initial=False)
    comment = forms.CharField(label=False, min_length=1, strip=True, widget=forms.Textarea(
        attrs={'id': 'user-comment-input', 'placeholder': 'Add comment...', 'rows': '0', 'cols': '0'}))


class TagsForm(forms.Form):
    """ Form for add/edit tags modal """
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(attrs={'value': 'TagsForm'}))
    # Need to use a CharField instead of BooleanField because
    # unchecked BooleanField just straight up don't get included in a request
    is_pinned = forms.CharField(label=False, required=True, initial="true", widget=forms.TextInput(attrs={'id': 'is-pinned-input'}))
    tagged_item = forms.CharField(label=False, required=True, widget=forms.TextInput(attrs={'id': 'item-id-input'}))
    public_tags = forms.CharField(label=False, required=False, initial="\\n", widget=forms.Textarea(attrs={'id': 'public-tags-form-field'}))
    private_tags = forms.CharField(label=False, required=False, initial="\\n", widget=forms.Textarea(attrs={'id': 'private-tags-form-field'}))
    # Need initial '\\n' for the isAlreadyAdded function in tag_modal.js
    total_points_for_item = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'id': 'total-points-for-item-field'}))


class ReportForm(forms.Form):
    """ Form for reporting a tag """
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(attrs={'value': 'ReportForm'}))
    reported_tag = forms.CharField(label=False, required=True,  widget=forms.TextInput(
        attrs={'id': 'reported-tag-input'}))
    is_irrelevant = forms.BooleanField(label="Irrelevant", required=False)  # Default to checkbox input field
    is_vulgar = forms.BooleanField(label="Vulgar", required=False)
    is_offensive = forms.BooleanField(label="Offensive", required=False)
    is_misinformation = forms.BooleanField(label="Misinformation / Disinformation", required=False)
    is_other = forms.BooleanField(label="Other", required=False)
    other_text = forms.CharField(label=False, required=False, min_length=1, max_length=999, widget=forms.TextInput(
        attrs={'id': 'other-input', 'placeholder': 'Please specify', 'label': 'If other, please specify'}))


class EquipForm(forms.Form):
    """ Form for equipping a title """
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(attrs={'value': 'EquipForm'}))
    if "tagme_reward" in connection.introspection.table_names():
        title_choices = list(Reward.objects.all().values_list('title', 'title'))  # pylint: disable=no-member
        title_choices.append(("Empty", "Empty"))
        title_choices = tuple(title_choices)
        title_to_equip = forms.ChoiceField(label=False, choices=title_choices,
                                           required=True, widget=forms.Select(attrs={'id': 'title-to-equip-input'}))
    equip_slot = forms.ChoiceField(label=False, choices=(("1", "1"), ("2", "2")), required=True,
                                   widget=forms.Select(attrs={'id': 'equip-slot-input'}))


class SignUpForm(UserCreationForm):  # pylint: disable=too-many-ancestors
    """
    Disabling pylint for ancestor error since this is best Django practice.
    Copied from: https://www.javatpoint.com/django-usercreationform
    With some modifications
    """
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(attrs={'value': 'SignUpForm'}))
    username = forms.CharField(label=False, min_length=1, max_length=150, widget=forms.TextInput(
        attrs={'class': 'signup-input', 'placeholder': 'Username', 'label': 'Username'}))
    email = forms.EmailField(label=False, widget=forms.EmailInput(
        attrs={'class': 'signup-input', 'placeholder': 'Email', 'label': 'Email'}))
    password1 = forms.CharField(label=False, widget=forms.PasswordInput(
        attrs={'class': 'signup-input', 'placeholder': 'Password', 'label': 'Password'}))
    password2 = forms.CharField(label=False, widget=forms.PasswordInput(
        attrs={'class': 'signup-input', 'placeholder': 'Confirm Password', 'label': 'Confirm Password'}))

    class Meta:  # pylint: disable=too-few-public-methods
        """Allows rearranging of form elements"""
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        """Prevents duplicate usernames (case-insensitive)"""
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(username=username)
        if new.count():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        """Prevents duplicate emails (case-insensitive)"""
        email = self.cleaned_data['email'].lower()
        new = User.objects.filter(email=email)
        if new.count():
            raise ValidationError("Email belongs to existing user.")
        return email

    def clean_password2(self):
        """Prevents mismatching password/confirms"""
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        """Saves cleaned data for the form"""
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user


class LoginForm(forms.Form):
    """Copied from https://medium.com/@devsumitg/django-auth-user-signup-and-login-7b424dae7fab"""
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(attrs={'value': 'LoginForm'}))
    username = forms.CharField(label=False, min_length=1, max_length=150, widget=forms.TextInput(
        attrs={'class': 'login-input', 'placeholder': 'Username', 'label': 'Username'}))
    password = forms.CharField(label=False, widget=forms.PasswordInput(
        attrs={'class': 'login-input', 'placeholder': 'Password', 'label': 'Password'}))

    def clean(self):
        """Ensures password and username match"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username').lower()
        password = cleaned_data.get('password')
        user = User.objects.filter(username=username)
        if user.count() == 0:
            self.add_error("username", "Username does not exist.")

        user = authenticate(username=username, password=password)
        if not user:
            self.add_error("password", "Password does not match our records.")
        return cleaned_data


class UsernameChangeForm(forms.Form):
    """
    Form to let users change their account's username.

    Each account setting is its own form because each field should be required if it's being changed
    (but not if another setting is being changed)
    """
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(
        attrs={'value': 'UsernameChangeForm', 'id': 'username_change_form_id_input'}))
    new_username = forms.CharField(label="New username", required=True, min_length=1, max_length=150,
                                   validators=[UnicodeUsernameValidator()],
                                   widget=forms.TextInput(attrs={'label': 'New username'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_username(self):
        """Prevents duplicate usernames (case-insensitive)"""
        new_username = self.cleaned_data['new_username'].lower()
        users = User.objects.filter(username=new_username)
        if users.count():
            raise ValidationError("Username already exists.")
        return new_username

    def save(self, commit=True):
        """Change the user's username when form is saved"""
        self.user.username = self.cleaned_data['new_username']
        if commit:
            self.user.save()
        return self.user


class EmailChangeForm(forms.Form):
    """
    Form to let users change their account's email address.

    Each account setting is its own form because each field should be required if it's being changed
    (but not if another setting is being changed)
    """
    # Need to specify id attribute of form_id because Django generates invalid HTML (duplicate id attributes) otherwise
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(
        attrs={'value': 'EmailChangeForm', 'id': 'email_change_form_id_input'}))
    new_email = forms.EmailField(label="New email address", required=True, widget=forms.EmailInput(
        attrs={'label': 'New email'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_email(self):
        """Prevents duplicate emails (case-insensitive)"""
        new_email = self.cleaned_data['new_email'].lower()
        users = User.objects.filter(email=new_email)
        if users.count():
            raise ValidationError("Email belongs to existing user.")
        return new_email

    def save(self, commit=True):
        """Change the user's email when form is saved"""
        self.user.email = self.cleaned_data['new_email']
        if commit:
            self.user.save()
        return self.user


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Form to let users change their account's email address.

    Overrides parts of default Django PasswordChangeForm.

    Each account setting is its own form because each field should be required if it's being changed
    (but not if another setting is being changed)
    """
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(
        attrs={'value': 'CustomPasswordChangeForm', 'id': 'password_change_form_id_input'}))
    PasswordChangeForm.base_fields['new_password2'].label = 'Confirm new password'  # pylint: disable=no-member


class DeleteAccountForm(forms.Form):
    """Form for deleting User account (i.e., User, UserProfile, and all other relevant model objects"""
    form_id = forms.CharField(label=False, widget=forms.HiddenInput(attrs={'value': 'DeleteAccountForm'}))
    delete_account = forms.BooleanField(label=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'invisible'}))
