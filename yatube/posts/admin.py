from typing import Tuple

from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display: Tuple[str, ...] = (
        'pk',
        'text',
        'created',
        'author',
        'group'
    )
    list_editable: Tuple[str, ...] = ('group',)
    search_fields: Tuple[str, ...] = ('text',)
    list_filter: Tuple[str, ...] = ('created',)
    empty_value_display: str = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)
