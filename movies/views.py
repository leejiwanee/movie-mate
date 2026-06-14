import requests
from django.shortcuts import render
from django.conf import settings

BASE_URL = 'https://api.themoviedb.org/3'

def trending_movies(request):
    url = f"{BASE_URL}/trending/movie/week?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    movies = response.json().get('results', [])
    return render(request, 'movies/trending.html', {'movies': movies})

def search_movies(request):
    query = request.GET.get('q')
    if not query:
        return render(request, 'movies/search.html', {'error': 'Please type the keywords.'})
    
    url = f"{BASE_URL}/search/movie?api_key={settings.TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    movies = response.json().get('results', [])
    return render(request, 'movies/search.html', {'movies': movies, 'query': query})