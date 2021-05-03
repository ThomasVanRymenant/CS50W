from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def __str__(self):
        return f'{self.username} (id:{self.id})'


class Post(models.Model):
    """A representation of a post inside the database"""

    content = models.TextField(max_length=800)
    created_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    likers = models.ManyToManyField(User, related_name='liking')

    def __str__(self):
        return f'post {self.id} posted by {self.creator}'


class Follow(models.Model):
    """A representation of a relationship between a user (A) and another user (B) who is following the user (A)"""

    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f"{self.follower} is following {self.followed_user}"