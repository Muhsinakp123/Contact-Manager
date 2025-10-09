from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
class Contact(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=150)
    email = models.EmailField()
    
    
    
    def __str__(self):
        return self.name
    

    def __str__(self):
        return f"{self.user}"