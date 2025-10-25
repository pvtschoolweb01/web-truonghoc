from django.db import models
from django.contrib.auth.models import User

class ClassPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)
    content = models.TextField()
    image = models.ImageField(upload_to="class_posts/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    #duyệt bài
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.class_name} - {self.author.username}: {self.content[:30]}"
