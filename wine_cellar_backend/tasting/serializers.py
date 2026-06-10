from rest_framework import serializers
from .models import TastingEvent, TastingAttendee, TastingNote
from collection.serializers import WineListSerializer, WineSerializer


class TastingEventSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    checked_in_count = serializers.IntegerField(read_only=True)
    registered_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    wine_list = WineListSerializer(source='wines', many=True, read_only=True)

    class Meta:
        model = TastingEvent
        fields = '__all__'
        read_only_fields = ['created_by']


class TastingEventListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    checked_in_count = serializers.IntegerField(read_only=True)
    registered_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    wine_count = serializers.IntegerField(source='wines.count', read_only=True)

    class Meta:
        model = TastingEvent
        fields = ['id', 'name', 'theme', 'event_date', 'location', 'organizer',
                  'status', 'status_display', 'max_attendees', 'created_by_name',
                  'checked_in_count', 'registered_count', 'average_rating',
                  'wine_count', 'created_at']


class TastingAttendeeSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = TastingAttendee
        fields = '__all__'

    def get_status_display(self, obj):
        return '已签到' if obj.checked_in else '未签到'


class TastingAttendeeListSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = TastingAttendee
        fields = ['id', 'name', 'phone', 'company', 'position',
                  'checked_in', 'check_in_time', 'status_display']

    def get_status_display(self, obj):
        return '已签到' if obj.checked_in else '未签到'


class TastingNoteSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    wine_name = serializers.CharField(source='wine.name', read_only=True)
    wine_vintage = serializers.IntegerField(source='wine.vintage', read_only=True)
    attendee_name = serializers.CharField(source='attendee.name', read_only=True)

    class Meta:
        model = TastingNote
        fields = '__all__'

    def validate(self, data):
        for field in ['color_rating', 'aroma_rating', 'taste_rating', 'finish_rating']:
            if field in data and (data[field] < 1 or data[field] > 5):
                raise serializers.ValidationError({field: '评分必须在1-5分之间'})
        return data


class TastingNoteListSerializer(serializers.ModelSerializer):
    wine_name = serializers.CharField(source='wine.name', read_only=True)
    wine_vintage = serializers.IntegerField(source='wine.vintage', read_only=True)
    attendee_name = serializers.CharField(source='attendee.name', read_only=True)

    class Meta:
        model = TastingNote
        fields = ['id', 'wine_name', 'wine_vintage', 'attendee_name',
                  'color_rating', 'aroma_rating', 'taste_rating', 'finish_rating',
                  'overall_rating', 'created_at']


class TastingEventStatsSerializer(serializers.Serializer):
    total_events = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()
    ongoing_events = serializers.IntegerField()
    completed_events = serializers.IntegerField()
    total_attendees = serializers.IntegerField()
    total_notes = serializers.IntegerField()
    avg_overall_rating = serializers.FloatField()
