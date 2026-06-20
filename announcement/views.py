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

        announcements = (
            Announcement.objects
            .filter(
                recipients=request.user ,
                is_active=True,
            )
            .prefetch_related("recipients")
        )

        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data)