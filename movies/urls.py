from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.trending_movies, name='trending'),
    path('search/', views.search_movies, name='search'),
]