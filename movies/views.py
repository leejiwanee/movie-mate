from pymongo import MongoClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
import requests

# TMDB API 기본 주소 설정
BASE_URL = 'https://api.themoviedb.org/3'
client = MongoClient('mongodb://localhost:27017/')
db = client['moviemate_db']
watchlist_collection = db['watchlist']

@csrf_exempt
def add_to_watchlist(request, movie_id):
    if request.method == "POST":
        title = request.POST.get('title', 'Unknown Title')
        if not watchlist_collection.find_one({"movie_id": movie_id}):
            watchlist_collection.insert_one({"movie_id": movie_id, "title": title, "watched": False})
        return JsonResponse({"status": "success", "message": "Added to Watchlist"})

def get_watchlist(request):
    movies = list(watchlist_collection.find({}, {'_id': 0}))
    return render(request, 'movies/watchlist.html', {'movies': movies})

def what_should_i_watch(request):
    url = f"{BASE_URL}/discover/movie?api_key={settings.TMDB_API_KEY}&sort_by=popularity.desc&vote_average.gte=7.5"
    response = requests.get(url)
    recommendations = response.json().get('results', [])[:5] 
    return render(request, 'movies/tonight.html', {'movies': recommendations})

def trending_movies(request):
    url = f"{BASE_URL}/trending/movie/day?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    movies = response.json().get('results', [])
    return render(request, 'movies/trending.html', {'movies': movies})

def search_movies(request):
    query = request.GET.get('q', '')
    movies = []
    if query:
        url = f"{BASE_URL}/search/movie?api_key={settings.TMDB_API_KEY}&query={query}"
        response = requests.get(url)
        movies = response.json().get('results', [])
    return render(request, 'movies/search.html', {'movies': movies, 'query': query})