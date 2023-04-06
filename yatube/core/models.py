from django.db import models


class BaseModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True)
    text = models.TextField('Текст', help_text='Введите текст')

    class Meta:
        abstract = True
