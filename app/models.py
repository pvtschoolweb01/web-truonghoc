from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL,null=True,blank=False)
    name = models.CharField(max_length=200,null=True)
    email = models.CharField(max_length=200,null=True)
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, editable=False, null=True, blank=True)
    
    full_name = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    class_name = models.CharField(max_length=4, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    typeuser = models.CharField(max_length=2, blank=True, null=True)
    sex = models.BooleanField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.jpg")

    def save(self, *args, **kwargs):
        self.username = self.user.username
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Profile of {self.user.username}"

class Thoikhoabieu(models.Model):
    lop = models.CharField(max_length=4,null=True)
    thu = models.IntegerField()
    buoi = models.CharField(max_length=4,null=False)
    tiet = models.IntegerField()
    mon = models.CharField(max_length=20,null=False)
    
    def __str__(self):
        return f"{self.lop}-{self.buoi}: Thứ {self.thu}, Tiết {self.tiet} = {self.mon}"
    
    class Meta:
        db_table = 'app_thoikhoabieu'
        
class MinigameAnswer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.answer[:20]}"
