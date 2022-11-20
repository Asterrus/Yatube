
from typing import Any, Dict, Optional, Type

from core.views import PostsListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Model
from django.forms import BaseForm, BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, View

from .forms import CommentForm, PostForm
from .models import Follow, Post, User


class IndexView(PostsListView):
    template_name: str = 'posts/index.html'

    def get_queryset(self):
        return Post.objects.select_related('group', 'author').all()


class GroupListView(PostsListView):
    template_name: str = 'posts/group_list.html'

    def get_queryset(self):
        return Post.objects.select_related('group', 'author').filter(
            group__slug=self.kwargs['group_slug'])


class ProfileView(PostsListView):
    template_name: str = 'posts/profile.html'

    def get_queryset(self):
        return Post.objects.select_related('group', 'author').filter(
            author__username=self.kwargs['username'])

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user.is_authenticated:
            follow = (self.request.user.follower.filter(author=author).exists()
                      or author == self.request.user)
            context['following'] = follow
        return context


class PostDetailView(DetailView):
    model: Optional[Type[Model]] = Post
    template_name: str = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        return get_object_or_404(
            Post.objects.select_related('author', 'group'),
            id=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class: Optional[Type[BaseForm]] = PostForm
    template_name: str = 'posts/post_create.html'

    def get_success_url(self, author):
        return reverse_lazy(
            'posts:profile',
            kwargs={'username': author.username})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        new_post = form.save(commit=False)
        new_post.author = self.request.user
        new_post.save()
        return redirect(self.get_success_url(new_post.author))


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name: str = 'posts/post_create.html'
    form_class: Optional[Type[BaseForm]] = PostForm
    pk_url_kwarg: str = 'post_id'

    def test_func(self) -> Optional[bool]:
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        if not self.request.user.is_authenticated:
            return redirect(
                '/auth/login/?next=' + reverse(
                    'posts:post_edit', kwargs={'post_id': post.pk}))
        return redirect(post.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        context["post"] = self.get_object()
        return context


class AddCommentView(LoginRequiredMixin, CreateView):
    form_class: Optional[Type[BaseForm]] = CommentForm
    pk_url_kwarg: str = 'post_id'

    def get(self, request: HttpRequest, *args: str, **kwargs: Any):
        post = get_object_or_404(Post, id=kwargs['post_id'])
        return redirect(post.get_absolute_url())

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        new_comment = form.save(commit=False)
        new_comment.author = self.request.user
        new_comment.post = post
        new_comment.save()
        return redirect(post.get_absolute_url())


class FollowIndex(LoginRequiredMixin, PostsListView):
    template_name: str = 'posts/follow.html'

    def get_queryset(self):
        return Post.objects.select_related('group', 'author').filter(
            author_id__in=self.request.user.follower.all(
            ).values_list('author_id'))


class ProfileFollowView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, *args: str, **kwargs: Any):
        author = get_object_or_404(User, username=kwargs['username'])
        if not (request.user.follower.filter(author=author).exists()
                or author == request.user):
            Follow(user=request.user, author=author).save()
        return redirect(reverse('posts:profile', args=[kwargs['username']]))


class ProfileUnfollowView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, *args: str, **kwargs: Any):
        author = get_object_or_404(User, username=kwargs['username'])
        Follow.objects.get(author=author, user=request.user).delete()
        return redirect(reverse('posts:profile', args=[kwargs['username']]))
