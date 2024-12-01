"""Module for defining models (i.e., SQLite3 database tables)"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Item(models.Model):
    """Class for Items database table"""
    item_id = models.TextField(primary_key=True, blank=False, null=False)  # The LOC API's item id

    def __str__(self):
        return self.item_id  # For proper display on admin site


class Tag(models.Model):
    """Class for Tags database table"""
    tag = models.TextField(primary_key=True, blank=False, null=False)
    global_blacklist = models.BooleanField(default=False)
    item_blacklist = models.ManyToManyField(Item, blank=True, related_name="blacklisted_for_items")
    global_whitelist = models.BooleanField(default=False)
    item_whitelist = models.ManyToManyField(Item, blank=True, related_name="whitelisted_for_items")

    def __str__(self):
        return self.tag  # For proper display on admin site


class Reward(models.Model):
    """Class for Rewards database table"""
    title = models.CharField(max_length=20, primary_key=True, blank=False, null=False)
    hex_colour = models.CharField(max_length=9, blank=False, null=False)  # hashtag + 6 to 8-digit hex code
    points_required = models.PositiveBigIntegerField(blank=False, null=False)

    def __str__(self):
        return self.title  # For proper display on admin site


class UserProfile(models.Model):
    """
    Class for UserProfile database table (extends default Django User model via OneToOneField)
    Reference: https://www.geeksforgeeks.org/how-to-extend-user-model-in-django/
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.PositiveBigIntegerField(default=0, blank=False, null=False)
    equipped_title_1 = models.ForeignKey(Reward, blank=True, null=True, related_name="title_1", on_delete=models.CASCADE)
    equipped_title_2 = models.ForeignKey(Reward, blank=True, null=True, related_name="title_2", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username  # For proper display on admin site


class UserContribution(models.Model):
    """
    Class for UserContributions database table
    Automatic "id" attribute is created as the table's primary key.
    """
    class Meta:
        # Ensure no duplicate entries for the same user on the same item
        constraints = [models.UniqueConstraint(fields=['user_id', 'item_id'], name='unique_user_contribution')]

    # on_delete=models.CASCADE --> will delete all relevant user contributions
    # if the user or item object in User or Items models is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # null=False && blank=False by default
    item = models.ForeignKey(Item, default=None, on_delete=models.CASCADE)

    # Default is false because contribution can exist for a comment without the user ever pinning the item
    is_pinned = models.BooleanField(default=False, blank=False, null=False)
    public_tags = models.ManyToManyField(Tag, blank=True, related_name="public_tags")
    private_tags = models.ManyToManyField(Tag, blank=True, related_name="private_tags")
    comment = models.TextField(blank=True, null=True)

    # Do NOT use auto_now=True because comment_datetime should not update if only tags are updated
    comment_datetime = models.DateTimeField(blank=True, null=True)

    def save_comment(self, *args, **kwargs):
        """Update timestamp when comment is added/edited"""
        self.comment_datetime = timezone.now()
        return super(UserContribution, self).save(*args, **kwargs)

    def __str__(self):
        username = User.objects.get(id=self.user_id).username
        return "User: " + username + ", Item: " + str(self.item_id)  # For proper display on admin site


class Report(models.Model):
    """Class for TagReports database table"""
    class ReportDecision(models.TextChoices):
        GLOBAL_BLACKLIST = "global_blacklist"
        ITEM_BLACKLIST = "item_blacklist"
        GLOBAL_WHITELIST = "global_whitelist"
        ITEM_WHITELIST = "item_whitelist"
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

    def save_decision(self, *args, **kwargs):
        """Update timestamp when decision is added/edited"""
        self.decision_datetime = timezone.now()
        return super(Report, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.report_id)
