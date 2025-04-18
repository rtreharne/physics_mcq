from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .utils.username_generator import generate_anonymous_username
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        name = generate_anonymous_username()
        # Ensure it's unique
        while Profile.objects.filter(anonymous_name=name).exists():
            name = generate_anonymous_username()
        Profile.objects.create(user=instance, anonymous_name=name)
