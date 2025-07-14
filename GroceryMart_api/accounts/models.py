from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    image = models.ImageField(upload_to='users/profile/', null=True, blank=True)
    balance = models.DecimalField(default= 0, max_digits= 12, decimal_places= 2)
    shopping_prefs = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.user.username 
    
    