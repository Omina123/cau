from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.db import models
from Ngoiso.models import Outstation
import random

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('1', 'Priest'),
        ('2', 'Chair'),
         ('3', "Catechist")
        
        
    )
    user_type = models.CharField(
        max_length=1,
        choices=USER_TYPE_CHOICES,
        default='2'
    )
    email = models.EmailField(unique=True)  # important for password reset
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()

class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Staff(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff')
    address = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
class Catechist(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='catechist')
    # Link to Outstation from Ngoiso app
    outstation = models.ForeignKey(
        Outstation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="catechists"
    )
    address = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Catechist: {self.admin.username}"
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == '1':
            Admin.objects.create(admin=instance)
        elif instance.user_type == '2':
            Staff.objects.create(admin=instance)
        elif instance.user_type == '3':
            # Creates the profile; outstation can be assigned later in the Admin panel
            Catechist.objects.create(admin=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == '1':
        if hasattr(instance, 'admin'):
            instance.admin.save()
    elif instance.user_type == '2':
        if hasattr(instance, 'staff'):
            instance.staff.save()
    elif instance.user_type == '3':
        if hasattr(instance, 'catechist'):
            instance.catechist.save()