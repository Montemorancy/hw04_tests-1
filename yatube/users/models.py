from django.db import models
from django.utils import timezone

from .validators import validate_not_empty


class Contact(models.Model):
    name = models.CharField(max_length=100, validators=[validate_not_empty])
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    body = models.TextField(validators=[validate_not_empty])
    is_answered = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.last_login:
            self.last_login = timezone.now()
        super().save(*args, **kwargs)
