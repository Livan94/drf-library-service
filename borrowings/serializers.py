from datetime import date

from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")
        read_only_fields = ("id",)

    def validate_book(self, value):
        if value.inventory < 1:
            raise serializers.ValidationError("Book is not available for borrowing.")
        return value

    def validate_expected_return_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError(
                "Expected return date must be later than today."
            )
        return value

    def create(self, validated_data):
        book = validated_data["book"]
        user = self.context["request"].user

        book.inventory -= 1
        book.save()

        return Borrowing.objects.create(user=user, **validated_data)
