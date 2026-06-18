from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Announcement
from .serializer import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.prefetch_related("recipients")
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def my_announcements(self, request):
        now = timezone.now()

        announcements = (
            Announcement.objects
            .filter(
                Q(recipients=request.user) |
                Q(recipients__isnull=True),
                is_active=True,
            )
            .filter(
                Q(start_at__isnull=True) | Q(start_at__lte=now),
                Q(end_at__isnull=True) | Q(end_at__gte=now),
            )
            .distinct()
            .prefetch_related("recipients")
        )

        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data)