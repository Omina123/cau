from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('1', 'Priest'),
        ('2', 'Chair'),
        
    )
    user_type = models.CharField(
        max_length=1,
        choices=USER_TYPE_CHOICES,
        default='2'
    )


class Admin(models.Model):
    id=models.AutoField(primary_key=True)
    admin= models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    #phone_number = PhoneNumberField(blank=True, null=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now_add=True)
    objects  = models.Manager() 
class Staff(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    id=models.AutoField(primary_key=True)
    address=models.CharField(max_length=200, blank=True, null=True)
    admin= models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now_add=True)
   
    objects=models.Manager()
    
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender,instance,created, **kwargs):
    if created:
        if instance.user_type==1:
            Admin.objects.create(admin=instance)
        if instance.user_type==2:
            Staff.objects.create(admin=instance)
        
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    elif instance.user_type == 2:
        if hasattr(instance, 'Staff'):  # Check if the user has a related Staff
            instance.Staff.save()
    
            