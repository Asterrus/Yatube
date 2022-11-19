from core.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()
POST_STR_NAME_LENGTH = 15


class Group(models.Model):
    """Group representation class."""
    title = models.CharField('Group name', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Description of the group')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(BaseModel):
    """Post representation class."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор', related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name='Группа', related_name='posts',
        help_text='Выбор группы, к которой относится текст'
    )
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)

    def __str__(self):
        return self.text[:POST_STR_NAME_LENGTH]

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"post_id": self.pk})

    class Meta:
        ordering = ['-created', 'text']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(BaseModel):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='comments',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        related_name='comments',
        on_delete=models.CASCADE
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )
