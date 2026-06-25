from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


@extend_schema(tags=["Books"])
@extend_schema_view(
    list=extend_schema(
        summary="List books",
        description="Retrieve a paginated list of all books available in the library.",
    ),
    retrieve=extend_schema(
        summary="Retrieve book",
        description="Retrieve detailed information about a specific book by its ID.",
    ),
    create=extend_schema(
        summary="Create book",
        description="Create a new book. Available only for admin users.",
    ),
    update=extend_schema(
        summary="Update book",
        description="Update all fields of an existing book. "
        "Available only for admin users.",
    ),
    partial_update=extend_schema(
        summary="Partially update book",
        description="Update selected fields of an existing book. "
        "Available only for admin users.",
    ),
    destroy=extend_schema(
        summary="Delete book",
        description="Delete a book from the library. Available only for admin users.",
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
