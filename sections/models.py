import secrets
import string
from django.conf import settings
from django.db import models


def generate_invite_code(length=8):
    """Generate a unique uppercase alphanumeric invite code (BR-03)."""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not Section.objects.filter(invite_code=code).exists():
            return code


class Section(models.Model):
    section_id = models.AutoField(primary_key=True)
    treasurer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        db_column='treasurer_id',
        related_name='managed_sections',
    )
    section_name = models.CharField(max_length=100)
    academic_term = models.CharField(max_length=50)
    invite_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sections'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = generate_invite_code()
        else:
            self.invite_code = self.invite_code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.section_name} ({self.academic_term})"