from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from .tasks import send_event_email
from django.contrib.auth import get_user_model
## В реальном проекте я бы использовал вот так, но так как это тестовое задание вместо почты поставлю заглушки
# User = get_user_model()
# recipient_list = User.objects.filter(is_active = True).values_list('email', flat=True)


@receiver(post_save, sender=Event)
def event_publish_email(sender, instance, created, **kwargs):
    if instance.status == 'PUBLISHED' and not created:
        recipient_list = ['test1@example.com', 'test2@example.com']
        subject = f'Новое мероприятие опубликовано: {instance.title}'
        message = f"Меропритие '{instance.title}' будет проходить {instance.start_datetime} в '{instance.venue.name}'"
        send_event_email.delay(subject, message, recipient_list)