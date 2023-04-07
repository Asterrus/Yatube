from typing import Optional

from django.shortcuts import render
from django.views.generic import ListView
from posts.models import Post

POSTS_ON_PAGE: int = 4


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)


class PostsListView(ListView):
    model = Post
    paginate_by: int = POSTS_ON_PAGE
    context_object_name: Optional[str] = 'posts'
