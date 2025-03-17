"""Module for registering models (i.e., SQLite3 database tables)"""

from django.contrib import admin
from django.http import JsonResponse
from .models import *
from .queries import update_tag_lists


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


class BlacklistedForItemsFilter(admin.SimpleListFilter):
    """Custom filter to allow filtering of tags that have at least 1 item in their item_blacklist"""
    title = "Blacklisted for # Items"
    parameter_name = "blacklisted_for_items"

    def lookups(self, request, model_admin):
        return [("yes", "Has at least 1 tag")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(item_blacklist=None)
        return queryset  # Return full queryset if no filter applied


class WhitelistedForItemsFilter(admin.SimpleListFilter):
    """Custom filter to allow filtering of tags that have at least 1 item in their item_whitelist"""
    title = "Whitelisted for # Items"
    parameter_name = "whitelisted_for_items"

    def lookups(self, request, model_admin):
        return [("yes", "Has at least 1 tag")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(item_whitelist=None)
        return queryset  # Return full queryset if no filter applied


########################################################################################################################

class ReportAdmin(admin.ModelAdmin):
    """Admin view for reporting. Creates display fields, filters, and then search fields for navigation."""
    change_form_template = 'admin_panel/report_change_form.html'
    list_display = ('report_id', 'item_id', 'user_id', 'tag', 'reason', 'creation_datetime', 'decision')
    list_filter = ('creation_datetime', DecisionFilter, 'user_id')
    search_fields = ('reason', 'user_id__username', 'tag__tag', 'item_id__item_id', 'item_id__title', 'decision')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        # If is AJAX request (i.e., so that JavaScript can check if need to display a warning message)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            item = Item.objects.get(item_id=request.POST['item_id'])
            old_tag = Tag.objects.get(tag=request.POST['tag'])
            user = User.objects.get(id=request.POST['user_id'])
            updated_report = Report(item_id=item, user_id=user, tag=old_tag, decision=request.POST['decision'], reason=request.POST['reason'])
            new_tag, new_ib, new_iw = update_tag_lists(updated_report, simulation=True, pre_save_report_id=request.POST['report_id'])

            simulated_new_tag = {'gb': new_tag.global_blacklist,   # New tag lists if update goes through
                                 'gw': new_tag.global_whitelist,
                                 'ib': item.item_id in new_ib,
                                 'iw': item.item_id in new_iw}

            tag_changes = {'gb_changed': old_tag.global_blacklist != simulated_new_tag['gb'],
                           'gw_changed': old_tag.global_whitelist != simulated_new_tag['gw'],
                           'ib_changed': old_tag.item_blacklist.filter(item_id=item).exists() != simulated_new_tag['ib'],
                           'iw_changed': old_tag.item_whitelist.filter(item_id=item).exists() != simulated_new_tag['iw']}

            return JsonResponse({'reported_tag': new_tag.tag,
                                 'new_tag': simulated_new_tag,
                                 'tag_changes': tag_changes})
        return super().changeform_view(request, object_id, form_url, extra_context)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'title', 'authors', 'publication_date')
    search_fields = ('item_id', 'title', 'authors', 'publication_date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required')


class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'global_blacklist', 'global_whitelist', 'item_blacklist_count', 'item_whitelist_count')
    list_filter = ('global_blacklist', 'global_whitelist', BlacklistedForItemsFilter, WhitelistedForItemsFilter)
    search_fields = ('tag', 'item_blacklist__item_id', 'item_blacklist__title', 'item_blacklist__authors',
                     'item_whitelist__item_id', 'item_whitelist__title', 'item_whitelist__authors')

    def item_blacklist_count(self, obj):
        return obj.item_blacklist.count()

    def item_whitelist_count(self, obj):
        return obj.item_whitelist.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    item_blacklist_count.short_description = "Blacklisted for # Items"
    item_whitelist_count.short_description = "Whitelisted for # Items"


# Register your models here.
admin.site.register(Report, ReportAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(UserProfile)
admin.site.register(UserContribution)
