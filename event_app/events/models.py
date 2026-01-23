from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Venue(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField() #широта
    longitude = models.FloatField() #долгота
    weather = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Event(models.Model):
    STATUS_CHOISES = [
        ('DRAFT','Draft'),
        ('PUBLISHED','Published'),
        ('CANCELLED','Cancelled')
    ]

    title = models.CharField(max_length=255)
    desk = models.TextField()
    publish_datetime = models.DateTimeField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(25)])
    status = models.CharField(max_length=20, choices=STATUS_CHOISES, default='DRAFT')
    

    def __str__(self):
        return self.title
    
class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_images/')
    preview = models.ImageField(upload_to='event_previews/', blank=True, null=True)

    def save(self, *args, **kwargs):
        from PIL import Image
        super().save(*args, **kwargs)
        if self.image and not self.preview:
            img = Image.open(self.image.path)
            img.thumbnail((200, 200))
            perview_path = self.image.path.replace('event_images', "event_previews")
            img.save(perview_path)
            self.preview = perview_path
            super().save(update_fields=['preview'])
    

