from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class User(AbstractUser):
    #Custom user model that extends Django's built-in user model
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class QRCode(models.Model):
    #Model for pre-generated QR Codes
    qr_code_data = models.CharField(max_length=255, unique=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='qr_codes')
    created_at = models.DateTimeField(auto_now_add=True)
    qr_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    
    def __str__(self):
        return f"QR Code: {self.qr_code_data}"
    
    def get_absolute_url(self):
        return reverse('qr_profile', kwargs={'qr_code_data': self.qr_code_data})
    
    @property
    def is_assigned(self):
        return self.assigned_to is not None

class EmergencyInfo(models.Model):
    #Model for user's emergency information
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('Unknown', 'Unknown'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='emergency_info')
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPES, default='Unknown')
    emergency_contacts = models.TextField(help_text="Format: Name - Relationship - Phone Number (one per line)")
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Emergency Info for {self.user.email}"
    
    def get_emergency_contacts_list(self):
        """Returns emergency contacts as a list of contacts"""
        if not self.emergency_contacts:
            return []
        return [contact.strip() for contact in self.emergency_contacts.split('\n') if contact.strip()]