from pymongo import MongoClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Please log in to save movies."})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
        title = data.get('title', 'Unknown Title')
        poster_path = data.get('poster_path', '')
        
        if not watchlist_collection.find_one({"movie_id": movie_id, "user_id": request.user.id}):
            watchlist_collection.insert_one({
                "user_id": request.user.id,
                "movie_id": movie_id, 
                "title": title, 
                "poster_path": poster_path,
                "watched": False
            })
            return JsonResponse({"status": "success", "message": f"'{title}' added to Watchlist!"})
        return JsonResponse({"status": "error", "message": f"'{title}' is already in your Watchlist."})

@csrf_exempt
def remove_from_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Please log in first."})

    if request.method == "POST":
        result = watchlist_collection.delete_one({"movie_id": movie_id, "user_id": request.user.id})
        if result.deleted_count > 0:
            return JsonResponse({"status": "success", "message": "Removed from Watchlist!"})
        return JsonResponse({"status": "error", "message": "Movie not found in Watchlist."})

@csrf_exempt
def toggle_watched(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Please log in first."})

    if request.method == "POST":
        movie = watchlist_collection.find_one({"movie_id": movie_id, "user_id": request.user.id})
        if movie:
            new_status = not movie.get('watched', False)
            watchlist_collection.update_one(
                {"movie_id": movie_id, "user_id": request.user.id}, 
                {"$set": {"watched": new_status}}
            )
            return JsonResponse({"status": "success", "message": "Watch status updated!", "watched": new_status})
        return JsonResponse({"status": "error", "message": "Movie not found."})

@csrf_exempt
def update_review(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Please log in first."})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
            
        rating = int(data.get('rating', 0))
        review_text = data.get('review_text', '').strip()
        
        movie = watchlist_collection.find_one({"movie_id": movie_id, "user_id": request.user.id})
        if movie:
            watchlist_collection.update_one(
                {"movie_id": movie_id, "user_id": request.user.id}, 
                {"$set": {"rating": rating, "review_text": review_text}}
            )
            return JsonResponse({"status": "success", "message": "Review saved successfully!"})
        return JsonResponse({"status": "error", "message": "Movie not found in Watchlist."})

@login_required(login_url='/accounts/login/')
def get_watchlist(request):
    filter_type = request.GET.get('filter', 'all')
    sort_type = request.GET.get('sort', 'newest')
    
    query = {"user_id": request.user.id}
    
    if filter_type == 'watched':
        query['watched'] = True
    elif filter_type == 'unwatched':
        query['watched'] = False
        
    sort_logic = [('_id', -1)]
    if sort_type == 'rating':
        sort_logic = [('rating', -1), ('_id', -1)]
    elif sort_type == 'title':
        sort_logic = [('title', 1)]
        
    cursor = watchlist_collection.find(query, {'_id': 0}).sort(sort_logic)
    movies = list(cursor)
    
    context = {
        'movies': movies,
        'current_filter': filter_type,
        'current_sort': sort_type
    }
    return render(request, 'movies/watchlist.html', context)

def what_should_i_watch(request):
    url = f"{BASE_URL}/discover/movie?api_key={settings.TMDB_API_KEY}&sort_by=popularity.desc&vote_average.gte=7.5"
    response = requests.get(url)
    recommendations = response.json().get('results', [])[:5] 
    return render(request, 'movies/tonight.html', {'movies': recommendations})

def trending_movies(request):
    url_p1 = f"{BASE_URL}/trending/movie/week?api_key={settings.TMDB_API_KEY}&page=1"
    response_p1 = requests.get(url_p1)
    movies = response_p1.json().get('results', [])
    
    url_p2 = f"{BASE_URL}/trending/movie/week?api_key={settings.TMDB_API_KEY}&page=2"
    response_p2 = requests.get(url_p2)
    movies.extend(response_p2.json().get('results', []))
    
    sort_type = request.GET.get('sort', 'trending')
    if sort_type == 'rating':
        movies.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
    elif sort_type == 'title':
        movies.sort(key=lambda x: x.get('title', ''))
    elif sort_type == 'newest':
        movies.sort(key=lambda x: x.get('release_date', ''), reverse=True)
        
    top_10 = movies[0:10] if len(movies) > 0 else []
    rest_movies = movies[10:] if len(movies) > 10 else []
        
    return render(request, 'movies/trending.html', {
        'top_10': top_10,
        'movies': rest_movies,
        'current_sort': sort_type
    })

def search_movies(request):
    query = request.GET.get('q', '')
    movies = []
    if query:
        url = f"{BASE_URL}/search/movie?api_key={settings.TMDB_API_KEY}&query={query}"
        response = requests.get(url)
        movies = response.json().get('results', [])
    return render(request, 'movies/search.html', {'movies': movies, 'query': query})

def movie_detail(request, movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={settings.TMDB_API_KEY}&append_to_response=credits,videos,similar"
    response = requests.get(url)
    movie = response.json()
    
    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = watchlist_collection.find_one({"movie_id": movie_id, "user_id": request.user.id}) is not None
        
    return render(request, 'movies/detail.html', {'movie': movie, 'in_watchlist': in_watchlist})