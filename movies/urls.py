from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.trending_movies, name='trending'),
    path('search/', views.search_movies, name='search'),
    path('watchlist/', views.get_watchlist, name='watchlist'),
    path('watchlist/add/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
]