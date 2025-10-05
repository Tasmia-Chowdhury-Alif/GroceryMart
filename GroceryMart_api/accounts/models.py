from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    postcode = models.CharField(max_length=50, null=True, blank=True)
    # image = models.ImageField(upload_to='accounts/profile/', null=True, blank=True)
    image = CloudinaryField('image', folder='grocerymart_images/accounts/avatars', null=True, blank=True)
    balance = models.DecimalField(default= 0, max_digits= 12, decimal_places= 2)
    shopping_prefs = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.user.username 
    
    