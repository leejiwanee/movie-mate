from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.trending_movies, name='trending'),
    path('search/', views.search_movies, name='search'),
    path('watchlist/', views.get_watchlist, name='watchlist'),
    path('watchlist/add/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/toggle/<int:movie_id>/', views.toggle_watched, name='toggle_watched'),
    path('watchlist/review/<int:movie_id>/', views.update_review, name='update_review'),
    path('tonight/', views.what_should_i_watch, name='tonight'),
    path('wrapped/', views.movie_wrapped, name='wrapped'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('diary/', views.movie_diary, name='diary'),
    path('calendar/', views.upcoming_calendar, name='calendar'),
    path('movie/<int:movie_id>/', views.movie_detail, name='detail'),
    path('watchlist/collection/<int:movie_id>/', views.update_collection, name='update_collection'),
]