from typing import List

from django.urls import path

from . import views

app_name: str = 'about'
urlpatterns: List[path] = [
    path('author/', views.AboutAuthor.as_view(), name='author'),
    path('tech/', views.AboutTech.as_view(), name='tech'),
]
