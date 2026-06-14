from pymongo import MongoClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
import requests
import json

# TMDB API 기본 주소 설정
BASE_URL = 'https://api.themoviedb.org/3'
client = MongoClient('mongodb://localhost:27017/')
db = client['moviemate_db']
watchlist_collection = db['watchlist']

@csrf_exempt
def add_to_watchlist(request, movie_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
        title = data.get('title', 'Unknown Title')
        poster_path = data.get('poster_path', '')
        
        if not watchlist_collection.find_one({"movie_id": movie_id}):
            watchlist_collection.insert_one({
                "movie_id": movie_id, 
                "title": title, 
                "poster_path": poster_path,
                "watched": False
            })
            return JsonResponse({"status": "success", "message": f"'{title}' added to Watchlist!"})
        return JsonResponse({"status": "error", "message": f"'{title}' is already in your Watchlist."})

@csrf_exempt
def remove_from_watchlist(request, movie_id):
    if request.method == "POST":
        result = watchlist_collection.delete_one({"movie_id": movie_id})
        if result.deleted_count > 0:
            return JsonResponse({"status": "success", "message": "Removed from Watchlist!"})
        return JsonResponse({"status": "error", "message": "Movie not found in Watchlist."})

@csrf_exempt
def toggle_watched(request, movie_id):
    if request.method == "POST":
        movie = watchlist_collection.find_one({"movie_id": movie_id})
        if movie:
            new_status = not movie.get('watched', False)
            watchlist_collection.update_one({"movie_id": movie_id}, {"$set": {"watched": new_status}})
            return JsonResponse({"status": "success", "message": "Watch status updated!", "watched": new_status})
        return JsonResponse({"status": "error", "message": "Movie not found."})

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