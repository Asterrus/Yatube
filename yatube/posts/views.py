from typing import Any, Dict, Optional, Type

from django.contrib.auth.decorators import login_required

from core.views import PostsListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Model
from django.forms import BaseForm, BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


class IndexView(PostsListView):
    template_name: str = 'posts/index.html'
    extra_context = {'title': 'Последние обновления на сайте'}

    def get_queryset(self):
        return Post.objects.select_related('group', 'author').all()


class GroupListView(PostsListView):
    template_name: str = 'posts/group_list.html'
    context_object_name = 'posts'
    extra_context = {'title': 'Записи сообщества: '}

    def get_queryset(self):
        return Post.objects.select_related('group', 'author').filter(
            group__slug=self.kwargs['group_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(Group, slug=self.kwargs['group_slug'])
        return context


class ProfileView(PostsListView):
    template_name: str = 'posts/profile.html'
    extra_context = {'title': 'Профайл пользователя: '}

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
        context['author'] = get_object_or_404(User, username=self.kwargs['username'])
        return context


class PostDetailView(DetailView):
    model: Optional[Type[Model]] = Post
    template_name: str = 'posts/post_detail.html'
    context_object_name = 'post'
    extra_context = {'card_title': 'Отправить комментарий', 'button_text': 'Отправить'}

    def get_object(self):
        return get_object_or_404(Post.objects.select_related('author', 'group'), id=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['action'] = reverse('posts:add_comment', args=(self.kwargs['post_id'],))
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class: Optional[Type[BaseForm]] = PostForm
    template_name: str = 'posts/post_create.html'
    extra_context = {'card_title': 'Создать пост', 'button_text': 'Создать', 'title': 'Создание поста'}

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
    extra_context = {'card_title': 'Редактировать пост', 'title': 'Редактирование поста', 'button_text': 'Подтвердить'}

    def test_func(self) -> Optional[bool]:
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        if not self.request.user.is_authenticated:
            return redirect(
                '/auth/login/?next=' + reverse(
                    'posts:post_edit', kwargs={'post_id': post.pk}))
        return redirect(post.get_absolute_url())


@login_required()
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return HttpResponseRedirect(post.get_absolute_url())
    post.delete()
    return redirect(reverse('posts:index'))


class AddCommentView(LoginRequiredMixin, CreateView):
    form_class: Optional[Type[BaseForm]] = CommentForm
    pk_url_kwarg: str = 'post_id'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        new_comment = form.save(commit=False)
        new_comment.author = self.request.user
        new_comment.post = post
        new_comment.save()
        return redirect(post.get_absolute_url())


class FollowIndex(LoginRequiredMixin, PostsListView):
    template_name: str = 'posts/follow.html'
    extra_context = {'title': 'Посты избранных авторов'}

    def get_queryset(self):
        return Post.objects.select_related('group', 'author').filter(
            author_id__in=self.request.user.follower.all(
            ).values_list('author_id'))


@login_required()
def follow(request, username):
    author = get_object_or_404(User, username=username)
    try:
        Follow.objects.create(user=request.user, author=author)
    finally:
        return redirect(reverse('posts:profile', kwargs={'username': username}))


@login_required()
def unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author)
    return redirect(reverse('posts:profile', kwargs={'username': username}))
