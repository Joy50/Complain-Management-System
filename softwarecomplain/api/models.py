from django.db import models
from authentication.models import CustomUser

# Create your models here.
class Software(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False)

    def __str__(self):
        return self.name

class Complain(models.Model):
    STATUS_CHOICE = [
        ("Initiated", "Initiated"),
        ("In_Progress", "In Progress"),
        ("Resolved", "Resolved"),
    ]
    
    software = models.ForeignKey(Software, on_delete=models.CASCADE, related_name='complaints')
    organization = models.CharField(max_length=255)
    referred_by = models.CharField(max_length=255, blank=True)
    problem_description = models.TextField()
    attached_document = models.FileField(upload_to='complaints/documents/', null=True, blank=True)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_complaints')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_complaints')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="initiated")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Complaint by {self.organization} on {self.software.name}"