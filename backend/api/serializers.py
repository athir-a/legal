from rest_framework import serializers


class AskRequestSerializer(serializers.Serializer):
    """
    Serializer to validate incoming legal question queries.
    """

    session_id = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=100,
        help_text="Optional session identifier for conversation tracking."
    )

    question = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=10000,
        error_messages={
            "required": "question field is required.",
            "blank": "question cannot be empty.",
        },
        help_text="The legal query submitted by the user."
    )

    language = serializers.ChoiceField(
        required=False,
        default="en",
        choices=["en", "ml"],
        help_text="Response language: en (English) or ml (Malayalam)."
    )

    def validate_question(self, value):
        trimmed = value.strip()

        if not trimmed:
            raise serializers.ValidationError(
                "question cannot be empty or contain only whitespace."
            )

        return trimmed