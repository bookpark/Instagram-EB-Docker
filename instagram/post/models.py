from django.conf import settings
from django.db import models


class PostManager(models.Manager):
    def get_queryset(self):
        return super(PostManager, self).get_queryset().exclude(author=None)


class Post(models.Model):
    # User model 불러오기
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # Admin에 접근하기 위해 blank 옵션을 줌
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    photo = models.ImageField(upload_to='post')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PostManager()

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        self.content = self.content
        return self.content
