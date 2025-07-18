from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserCounter

@receiver(post_save, sender=User)
def create_user_counter(sender, instance, created, **kwargs):
    if created:
        UserCounter.objects.create(user=instance)