from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Avg
from .models import TastingEvent, TastingAttendee, TastingNote
from .serializers import (
    TastingEventSerializer, TastingEventListSerializer,
    TastingAttendeeSerializer, TastingAttendeeListSerializer,
    TastingNoteSerializer, TastingNoteListSerializer,
    TastingEventStatsSerializer
)


class TastingEventViewSet(viewsets.ModelViewSet):
    queryset = TastingEvent.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TastingEventListSerializer
        return TastingEventSerializer

    def get_queryset(self):
        queryset = TastingEvent.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        for event in queryset:
            event.update_status_based_on_time()
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        event = self.get_object()
        phone = request.data.get('phone')
        name = request.data.get('name')

        if not phone and not name:
            return Response({'error': '请提供手机号或姓名'}, status=status.HTTP_400_BAD_REQUEST)

        attendee = None
        if phone:
            try:
                attendee = event.attendees.get(phone=phone)
            except TastingAttendee.DoesNotExist:
                pass

        if not attendee and name:
            try:
                attendee = event.attendees.get(name=name)
            except TastingAttendee.DoesNotExist:
                pass

        if not attendee:
            if event.registered_count() >= event.max_attendees:
                return Response({'error': '参会人数已达上限'}, status=status.HTTP_400_BAD_REQUEST)
            attendee = TastingAttendee.objects.create(
                event=event,
                name=name or '临时参会',
                phone=phone or ''
            )

        attendee.do_check_in()
        return Response(TastingAttendeeSerializer(attendee).data)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        if event.registered_count() >= event.max_attendees:
            return Response({'error': '报名人数已达上限'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TastingAttendeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        event = self.get_object()
        attendees = event.attendees.all()
        checked_in = request.query_params.get('checked_in')
        if checked_in == 'true':
            attendees = attendees.filter(checked_in=True)
        elif checked_in == 'false':
            attendees = attendees.filter(checked_in=False)
        return Response(TastingAttendeeListSerializer(attendees, many=True).data)

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        event = self.get_object()
        notes = event.tasting_notes.all()
        return Response(TastingNoteListSerializer(notes, many=True).data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        event = self.get_object()
        notes = event.tasting_notes.all()

        wine_stats = []
        for wine in event.wines.all():
            wine_notes = notes.filter(wine=wine)
            if wine_notes:
                wine_stats.append({
                    'wine_id': wine.id,
                    'wine_name': wine.name,
                    'wine_vintage': wine.vintage,
                    'note_count': wine_notes.count(),
                    'avg_color': round(wine_notes.aggregate(Avg('color_rating'))['color_rating__avg'] or 0, 1),
                    'avg_aroma': round(wine_notes.aggregate(Avg('aroma_rating'))['aroma_rating__avg'] or 0, 1),
                    'avg_taste': round(wine_notes.aggregate(Avg('taste_rating'))['taste_rating__avg'] or 0, 1),
                    'avg_finish': round(wine_notes.aggregate(Avg('finish_rating'))['finish_rating__avg'] or 0, 1),
                    'avg_overall': round(wine_notes.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0, 1),
                })

        return Response({
            'registered_count': event.registered_count(),
            'checked_in_count': event.checked_in_count(),
            'note_count': notes.count(),
            'avg_overall_rating': event.average_rating(),
            'wine_stats': wine_stats,
        })


class TastingAttendeeViewSet(viewsets.ModelViewSet):
    queryset = TastingAttendee.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TastingAttendeeListSerializer
        return TastingAttendeeSerializer

    def get_queryset(self):
        queryset = TastingAttendee.objects.all()
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        attendee = self.get_object()
        attendee.do_check_in()
        return Response(TastingAttendeeSerializer(attendee).data)


class TastingNoteViewSet(viewsets.ModelViewSet):
    queryset = TastingNote.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TastingNoteListSerializer
        return TastingNoteSerializer

    def get_queryset(self):
        queryset = TastingNote.objects.all()
        event_id = self.request.query_params.get('event')
        wine_id = self.request.query_params.get('wine')
        attendee_id = self.request.query_params.get('attendee')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        if wine_id:
            queryset = queryset.filter(wine_id=wine_id)
        if attendee_id:
            queryset = queryset.filter(attendee_id=attendee_id)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            attendee = TastingAttendee.objects.get(id=data.get('attendee'))
            if not attendee.checked_in:
                return Response({'error': '请先完成签到再提交品鉴笔记'}, status=status.HTTP_400_BAD_REQUEST)
        except TastingAttendee.DoesNotExist:
            return Response({'error': '参会人员不存在'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


class TastingStatsViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def overview(self, request):
        events = TastingEvent.objects.all()
        for event in events:
            event.update_status_based_on_time()

        total_events = events.count()
        upcoming_events = events.filter(status='upcoming').count()
        ongoing_events = events.filter(status='ongoing').count()
        completed_events = events.filter(status='completed').count()

        total_attendees = TastingAttendee.objects.count()
        total_notes = TastingNote.objects.count()
        avg_rating = TastingNote.objects.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0

        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[str(i)] = TastingNote.objects.filter(overall_rating__gte=i, overall_rating__lt=i + 1).count()

        recent_events = events.order_by('-event_date')[:5]

        return Response({
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'completed_events': completed_events,
            'total_attendees': total_attendees,
            'total_notes': total_notes,
            'avg_overall_rating': round(avg_rating, 1),
            'rating_distribution': rating_distribution,
            'recent_events': TastingEventListSerializer(recent_events, many=True).data,
        })
