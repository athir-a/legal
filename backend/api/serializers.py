from rest_framework import serializers


class AskRequestSerializer(serializers.Serializer):
    """
    Serializer to validate incoming legal question queries.
    Ensures that 'question' is provided and not empty.
    """
    session_id = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional session identifier for conversation tracking."
    )
    question = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            'required': 'question field is required.',
            'blank': 'question cannot be empty.',
        },
        help_text="The legal query submitted by the user."
    )

    def validate_question(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("question cannot be empty or contain only whitespace.")
        return trimmed
