"""Module for defining models (i.e., SQLite3 database tables)"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Item(models.Model):
    """Class for Items database table"""
    item_id = models.TextField(primary_key=True, blank=False, null=False)  # The LOC API's item id
    title = models.TextField(blank=False, null=False, default="No title available")
    authors = models.TextField(blank=False, null=False, default="Unknown")
    publication_date = models.TextField(blank=False, null=False, default="No publication date available")
    description = models.TextField(blank=False, null=False, default="No description available")
    _subjects = models.TextField(db_column='subjects', blank=True, null=True)  # String representing a list with \n delimitor
    cover = models.TextField(blank=True, null=True)

    @property
    def subjects(self):
        """Automatically convert _subjects (str) into a list of strings when accessing subjects"""
        if isinstance(self._subjects, str):
            return self._subjects.split("\\n")
        return self._subjects

    @subjects.setter
    def subjects(self, subject_list):
        """
        Automatically convert a list of strings into a single str with '\n' delimiter
        & store this str in _subjects model field
        """
        if isinstance(subject_list, list):
            self._subjects = '\\n'.join(subject_list)
        else:
            self._subjects = subject_list

    def __str__(self):
        return str(self.item_id)  # For proper display on admin site


class Tag(models.Model):
    """Class for Tags database table"""
    tag = models.TextField(primary_key=True, blank=False, null=False)
    global_blacklist = models.BooleanField(default=False)
    item_blacklist = models.ManyToManyField(Item, blank=True, related_name="blacklisted_for_items")
    global_whitelist = models.BooleanField(default=False)
    item_whitelist = models.ManyToManyField(Item, blank=True, related_name="whitelisted_for_items")

    def __str__(self):
        return str(self.tag)  # For proper display on admin site


class Reward(models.Model):
    """Class for Rewards database table"""
    title = models.CharField(max_length=20, primary_key=True, blank=False, null=False)
    hex_colour = models.CharField(max_length=9, blank=False, null=False)  # hashtag + 6 to 8-digit hex code
    points_required = models.PositiveBigIntegerField(blank=False, null=False)

    def __str__(self):
        return str(self.title)  # For proper display on admin site


class UserContribution(models.Model):
    """
    Class for UserContributions database table
    Automatic "id" attribute is created as the table's primary key.
    """
    class Meta:
        """Meta class for UserContribution model"""
        # Ensure no duplicate entries for the same user on the same item
        constraints = [models.UniqueConstraint(fields=['user_id', 'item_id'], name='unique_user_contribution')]

    # on_delete=models.CASCADE --> will delete all relevant user contributions
    # if the user or item object in User or Items models is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # null=False && blank=False by default
    item = models.ForeignKey(Item, default=None, on_delete=models.CASCADE)

    # Default is false because contribution can exist for a comment without the user ever pinning the item
    # Do NOT use auto_now=True because pin_datetime should not update if a tag/comment is updated, but pin status doesn't change
    is_pinned = models.BooleanField(default=False, blank=False, null=False)
    pin_datetime = models.DateTimeField(blank=True, null=True)  # Can be blank && null because comment can exist without pin

    public_tags = models.ManyToManyField(Tag, blank=True, related_name="public_tags")
    private_tags = models.ManyToManyField(Tag, blank=True, related_name="private_tags")
    points_earned = models.IntegerField(default=0, blank=False, null=False)  # To prevent point farming by deleting/re-adding

    comment = models.TextField(blank=True, null=True)
    comment_datetime = models.DateTimeField(blank=True, null=True)
    # Do NOT use auto_now=True because comment_datetime should not update if only tags are updated

    def save_comment(self, *args, **kwargs):
        """Update timestamp when comment is added/edited"""
        self.comment_datetime = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "User: " + str(self.user) + ", Item: " + str(self.item)  # For proper display on admin site


class UserProfile(models.Model):
    """
    Class for UserProfile database table (extends default Django User model via OneToOneField)
    Reference: https://www.geeksforgeeks.org/how-to-extend-user-model-in-django/

    Note: MUST BE PLACED AFTER UserContribution MODEL (!!!!!!) so that objects are deleted in
    the correct order if a User is deleted from the database.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.PositiveBigIntegerField(default=0, blank=False, null=False)
    equipped_title_1 = models.ForeignKey(Reward, blank=True, null=True, related_name="title_1", on_delete=models.CASCADE)
    equipped_title_2 = models.ForeignKey(Reward, blank=True, null=True, related_name="title_2", on_delete=models.CASCADE)

    def update_points(self):
        """ Sum all points_earned from UserContribution (for that user) """
        total_points = self.user.usercontribution_set.aggregate(total=models.Sum('points_earned'))['total'] or 0  # pylint: disable=no-member
        self.points = total_points
        self.save()

    def __str__(self):
        return str(self.user)  # For proper display on admin site


class Report(models.Model):
    """Class for TagReports database table"""
    class ReportDecision(models.TextChoices):
        """Admin decision options for tag reports"""
        GLOBAL_BLACKLIST = "global_blacklist"
        ITEM_BLACKLIST = "item_blacklist"
        GLOBAL_WHITELIST = "global_whitelist"
        ITEM_WHITELIST = "item_whitelist"
        IGNORE_REPORT = "ignore_report"
        # ReportDecision.GLOBAL_BLACKLIST.label --> returns "Global Blacklist"

    report_id = models.BigAutoField(primary_key=True, blank=False, null=False)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)  # null=False && blank=False by default
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField(blank=False, null=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)  # Datetime cannot be overwritten / manually set
    decision = models.CharField(max_length=16, blank=True, null=True, choices=ReportDecision)
    decision_datetime = models.DateTimeField(blank=True, null=True)
    # Do NOT use auto_now=True because decision_datetime should not be set when report is first created

    def save(self, *args, **kwargs):
        if self.decision:  # If new decision has been made, set decision_datetime to now
            self.decision_datetime = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.report_id)
