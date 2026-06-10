from django.contrib import admin
from .models import TastingEvent, TastingAttendee, TastingNote


class TastingAttendeeInline(admin.TabularInline):
    model = TastingAttendee
    extra = 0
    fields = ('name', 'phone', 'company', 'checked_in', 'check_in_time')
    readonly_fields = ('check_in_time',)


class TastingNoteInline(admin.TabularInline):
    model = TastingNote
    extra = 0
    fields = ('wine', 'attendee', 'color_rating', 'aroma_rating', 'taste_rating', 'finish_rating', 'overall_rating')
    readonly_fields = ('overall_rating',)


@admin.register(TastingEvent)
class TastingEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'theme', 'event_date', 'location', 'status', 'registered_count', 'checked_in_count', 'average_rating')
    list_filter = ('status', 'event_date', 'organizer')
    search_fields = ('name', 'theme', 'location', 'organizer')
    inlines = [TastingAttendeeInline, TastingNoteInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'theme', 'description', 'event_date', 'location', 'organizer')
        }),
        ('配置', {
            'fields': ('max_attendees', 'wines', 'status', 'notes')
        }),
        ('系统信息', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def registered_count(self, obj):
        return obj.registered_count()
    registered_count.short_description = '报名人数'

    def checked_in_count(self, obj):
        return obj.checked_in_count()
    checked_in_count.short_description = '签到人数'


@admin.register(TastingAttendee)
class TastingAttendeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'phone', 'company', 'position', 'checked_in', 'check_in_time')
    list_filter = ('checked_in', 'event')
    search_fields = ('name', 'phone', 'company', 'email')
    actions = ['do_check_in']

    def do_check_in(self, request, queryset):
        for attendee in queryset:
            attendee.do_check_in()
        self.message_user(request, f'成功为 {queryset.count()} 位参会者签到')
    do_check_in.short_description = '批量签到'


@admin.register(TastingNote)
class TastingNoteAdmin(admin.ModelAdmin):
    list_display = ('attendee', 'wine', 'event', 'color_rating', 'aroma_rating', 'taste_rating', 'finish_rating', 'overall_rating')
    list_filter = ('event', 'wine')
    search_fields = ('attendee__name', 'wine__name', 'general_notes')
    readonly_fields = ('overall_rating', 'created_at')
