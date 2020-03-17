from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CSUser(AbstractUser):
    pass


class CSUserProfile(models.Model):

    user = models.OneToOneField(CSUser, unique=True, null=False, db_index=True, on_delete=models.CASCADE)

    @receiver(post_save, sender=CSUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            CSUserProfile.objects.create(user=instance)

    @receiver(post_save, sender=CSUser)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()
