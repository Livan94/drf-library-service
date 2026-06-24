from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer, BorrowingCreateSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Borrowing.objects.select_related("book", "user")

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.save()

        read_serializer = BorrowingReadSerializer(
            borrowing,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(read_serializer.data)

        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
