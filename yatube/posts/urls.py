from django.urls import path

from .views import (AddCommentView, FollowIndex, GroupListView, IndexView,
                    PostCreateView, post_delete, PostDetailView, PostEditView,
                    follow, ProfileView, unfollow)

app_name: str = 'posts'
urlpatterns: list = [
    path('', IndexView.as_view(), name='index'),
    path('group/<slug:group_slug>/', GroupListView.as_view(), name='group_list'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:post_id>/delete/', post_delete, name='post_delete'),
    path('posts/<int:post_id>/edit/', PostEditView.as_view(), name='post_edit'),
    path('posts/<int:post_id>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('follow/', FollowIndex.as_view(), name='follow_index'),
    path('profile/<str:username>/follow/', follow, name='profile_follow'),
    path('profile/<str:username>/unfollow/', unfollow, name='profile_unfollow'),
]
