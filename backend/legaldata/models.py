from django.db import models


class LegalDocument(models.Model):
    act_id = models.CharField(max_length=255)
    act_title = models.CharField(max_length=500)
    section_number = models.CharField(max_length=50)
    section_title = models.CharField(max_length=500)
    chapter = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField()
    status = models.CharField(max_length=50, blank=True)
    year = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=255)
    source_url = models.URLField(max_length=1000, blank=True)

    def __str__(self):
        return f"{self.act_title} - Section {self.section_number}"


class LegalChunk(models.Model):
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.CASCADE,
        related_name="chunks"
    )
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()

    def __str__(self):
        return (
            f"{self.document.act_title} - "
            f"Section {self.document.section_number} - "
            f"Chunk {self.chunk_index}"
        )


class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_id


class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    question = models.TextField()
    answer = models.TextField()
    supported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.session_id} - {self.created_at}"