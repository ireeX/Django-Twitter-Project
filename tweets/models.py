from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

import pytz


class Tweet(models.Model):
    content = models.TextField(max_length=255)
    # who posts this tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def hours_to_now(self):
        return (datetime.now(tz=pytz.utc) - self.created_at).seconds // 3600

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'