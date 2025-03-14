"""Module for registering models (i.e., SQLite3 database tables)"""

from django.contrib import admin
from .models import *


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
    search_fields = ('reason', 'user_id__username', 'tag__tag', 'item_id__item_id', 'item_id__title', 'decision')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        report = self.get_object(request, object_id)  # Get the report being edited
        if report:
            other_tag_reports = (Report.objects
                                 .filter(tag=report.tag)
                                 .exclude(report_id=report.report_id)
                                 .order_by('-decision_datetime')
                                 .values("report_id", "decision", "item_id"))

            # Pass all other reports for the same tag when the page is OPENED (NOT when "Save" button is clicked)
            # Need to convert reported_tag's data to HTML/Django readable value
            reported_tag = {
                'tag': report.tag.tag,
                'global_blacklist': str(report.tag.global_blacklist),
                'global_whitelist': str(report.tag.global_whitelist),
                'has_any_in_item_blacklist': "True" if report.tag.item_blacklist.exists() else "False",
                'has_item_in_item_blacklist': "True" if report.tag.item_blacklist.filter(item_id=report.item_id).exists() else "True",
                'has_any_in_item_whitelist': "True" if report.tag.item_whitelist.exists() else "False",
                'has_item_in_item_whitelist': "True" if report.tag.item_whitelist.filter(item_id=report.item_id).exists() else "False"
            }

            extra_context["reported_tag"] = reported_tag

            if other_tag_reports:
                extra_context["other_tag_reports"] = list(other_tag_reports)
        return super().change_view(request, object_id, form_url, extra_context)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'title', 'authors', 'publication_date')
    search_fields = ('item_id', 'title', 'authors', 'publication_date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required')


# Register your models here.
admin.site.register(Report, ReportAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Tag)
admin.site.register(Reward, RewardAdmin)
admin.site.register(UserProfile)
admin.site.register(UserContribution)
