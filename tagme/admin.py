"""Module for registering models (i.e., SQLite3 database tables)"""

from django.contrib import admin
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from .models import *

# Register your models here.
admin.site.register(Item)
admin.site.register(Tag)
admin.site.register(Reward)
admin.site.register(UserProfile)
admin.site.register(UserContribution)


class DecisionFilter(admin.SimpleListFilter):
    """Custom filter to allow filtering of reports that don't have a decision"""
    title = "decision"
    parameter_name = "decision"

    def lookups(self, request, model_admin):
        return (
            (Report.ReportDecision.GLOBAL_BLACKLIST, 'Global Blacklist'),
            (Report.ReportDecision.ITEM_BLACKLIST, 'Item Blacklist'),
            (Report.ReportDecision.GLOBAL_WHITELIST, 'Global Whitelist'),
            (Report.ReportDecision.ITEM_WHITELIST, 'Item Whitelist'),
            (Report.ReportDecision.IGNORE_REPORT, 'Ignore Report'),
            ('new_report', 'New Reports')
        )

    def queryset(self, request, queryset):
        if self.value() == 'new_report':
            return queryset.filter(decision__isnull=True)
        elif self.value():
            return queryset.filter(decision=self.value())
        return queryset


class ReportAdmin(admin.ModelAdmin):
    """Admin view for reporting. Creates display fields, filters, and then search fields for navigation."""
    change_form_template = 'admin_panel/report_change_form.html'
    list_display = ('report_id', 'item_id', 'user_id', 'tag', 'reason', 'creation_datetime', 'decision')
    list_filter = ('creation_datetime', DecisionFilter, 'user_id')
    search_fields = ('reason', 'user_id__username', 'tag__tag')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        report = self.get_object(request, object_id)  # Get the report being edited
        if report:
            # NOTE: Impossible for users to report tags that are globally banned by default
            # All other global bans/allows can (should) only be set via a previous report

            # NOTE: Message should appear if trying to whitelist a tag that's been globally blacklisted (regardless of item)
            # TODO

            # NOTE: Message should appear if trying to blacklist a tag that's been globally whitelisted (regardless of item)
            # TODO

            # TODO: Do not show message if prev decision is Ignore Report or null? (filter out identical report with Ignore Report decision? (null not counted by system already/by default?))
            # TODO: Do not show message if new decision is Ignore Report or null? (JavaScript)

            # NOTE: Changing back to null decision == does NOT reset Tag object
            # NOTE: Clicking "Ignore Report" == reset Tag object EVEN IF prev report still has valid decision
            # TODO (see Models TODO): Sync tag decision to most recent decision for that tag (that isn't null or Ignore Report) --> if none, then reset Tag object

            identical_reports = (Report.objects
                                 .filter(item_id=report.item_id, tag=report.tag)
                                 .exclude(report_id=report.report_id)  # Exclude the current report being edited
                                 .values("report_id", "decision"))

            # Pass all identical reports when the page is OPENED (NOT when "Save" button is clicked)
            extra_context["identical_reports"] = list(identical_reports)
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(Report, ReportAdmin)
