import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Ticket


@receiver(post_delete, sender=Ticket)
def delete_ticket_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(pre_save, sender=Ticket)
def delete_old_ticket_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)
