from pymongo import MongoClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
import json
import random
from collections import Counter
from datetime import datetime

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
        
        genres = []
        try:
            url = f"{BASE_URL}/movie/{movie_id}?api_key={settings.TMDB_API_KEY}"
            response = requests.get(url)
            movie_data = response.json()
            if 'genres' in movie_data:
                genres = [g['name'] for g in movie_data['genres']]
        except Exception:
            pass
            
        if not watchlist_collection.find_one({"movie_id": movie_id, "user_id": request.user.id}):
            watchlist_collection.insert_one({
                "user_id": request.user.id,
                "movie_id": movie_id, 
                "title": title, 
                "poster_path": poster_path,
                "genres": genres,
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
    collection_filter = request.GET.get('collection', None)
    
    query = {"user_id": request.user.id}
    
    if collection_filter:
        query['custom_collections'] = collection_filter
    
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
    
    collections_list = watchlist_collection.distinct("custom_collections", {"user_id": request.user.id})
    collections_list = [c for c in collections_list if c]
    
    context = {
        'movies': movies,
        'current_filter': filter_type,
        'current_sort': sort_type,
        'current_collection': collection_filter,
        'collections_list': collections_list
    }
    return render(request, 'movies/watchlist.html', context)

@csrf_exempt
@login_required(login_url='/accounts/login/')
def update_collection(request, movie_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
            
        action = data.get('action')
        collection_name = data.get('collection_name', '').strip()
        
        if not collection_name:
            return JsonResponse({"status": "error", "message": "Collection name cannot be empty."})
            
        movie = watchlist_collection.find_one({"movie_id": movie_id, "user_id": request.user.id})
        if movie:
            if action == 'add':
                watchlist_collection.update_one(
                    {"movie_id": movie_id, "user_id": request.user.id},
                    {"$addToSet": {"custom_collections": collection_name}}
                )
                return JsonResponse({"status": "success", "message": f"Added to '{collection_name}'!"})
            elif action == 'remove':
                watchlist_collection.update_one(
                    {"movie_id": movie_id, "user_id": request.user.id},
                    {"$pull": {"custom_collections": collection_name}}
                )
                return JsonResponse({"status": "success", "message": f"Removed from '{collection_name}'!"})
                
        return JsonResponse({"status": "error", "message": "Movie not found in Watchlist."})
    return JsonResponse({"status": "error", "message": "Invalid request method."})

@login_required(login_url='/accounts/login/')
def what_should_i_watch(request):
    unwatched_cursor = watchlist_collection.find({"user_id": request.user.id, "watched": False}, {"_id": 0})
    pool = list(unwatched_cursor)
    
    if len(pool) < 15:
        url = f"{BASE_URL}/trending/movie/week?api_key={settings.TMDB_API_KEY}"
        try:
            response = requests.get(url)
            trending = response.json().get('results', [])
            for t in trending:
                mapped = {
                    "movie_id": t.get("id"),
                    "title": t.get("title"),
                    "poster_path": t.get("poster_path"),
                    "overview": t.get("overview")
                }
                if not any(m.get('movie_id') == mapped['movie_id'] for m in pool):
                    pool.append(mapped)
        except Exception:
            pass
            
    random.shuffle(pool)
    
    return render(request, 'movies/tonight.html', {
        'movies_json': json.dumps(pool)
    })

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

@login_required(login_url='/accounts/login/')
def dashboard(request):
    user_id = request.user.id
    
    total_count = watchlist_collection.count_documents({"user_id": user_id})
    watched_count = watchlist_collection.count_documents({"user_id": user_id, "watched": True})
    unwatched_count = total_count - watched_count
    
    rated_movies = list(watchlist_collection.find({"user_id": user_id, "rating": {"$gt": 0}}, {"rating": 1, "_id": 0}))
    average_rating = 0
    if rated_movies:
        average_rating = sum([m.get('rating', 0) for m in rated_movies]) / len(rated_movies)
        
    top_rated_cursor = watchlist_collection.find({"user_id": user_id, "rating": {"$gt": 0}}).sort("rating", -1).limit(5)
    top_rated = list(top_rated_cursor)
    
    recent_cursor = watchlist_collection.find({"user_id": user_id}).sort("_id", -1).limit(5)
    recently_added = list(recent_cursor)
    
    progress_percentage = 0
    if total_count > 0:
        progress_percentage = int((watched_count / total_count) * 100)
        
    genre_counter = Counter()
    for m in watchlist_collection.find({"user_id": user_id}):
        if 'genres' in m and m['genres']:
            for g in m['genres']:
                genre_counter[g] += 1
                
    top_genres = genre_counter.most_common(5)
    genre_labels = [g[0] for g in top_genres]
    genre_data = [g[1] for g in top_genres]
    
    # Achievements Calculation
    earned_badges = []
    locked_badges = []
    total_reviews = watchlist_collection.count_documents({"user_id": user_id, "review_text": {"$exists": True, "$ne": ""}})
    
    badges = [
        {"icon": "🎬", "title": "First Blood", "desc": "Added 1st movie", "unlocked": total_count >= 1},
        {"icon": "🍿", "title": "Cinephile", "desc": "Watched 10 movies", "unlocked": watched_count >= 10},
        {"icon": "✍️", "title": "The Critic", "desc": "Wrote 3 reviews", "unlocked": total_reviews >= 3},
        {"icon": "💯", "title": "Completionist", "desc": "100% Watched (min 5)", "unlocked": progress_percentage == 100 and total_count >= 5},
        {"icon": "🦸‍♂️", "title": "Action Hero", "desc": "Watched 3 Action movies", "unlocked": genre_counter.get('Action', 0) >= 3},
        {"icon": "🛸", "title": "Sci-Fi Explorer", "desc": "Watched 3 Sci-Fi movies", "unlocked": genre_counter.get('Science Fiction', 0) >= 3},
    ]
    
    for b in badges:
        if b['unlocked']:
            earned_badges.append(b)
        else:
            locked_badges.append(b)
        
    context = {
        'total_count': total_count,
        'watched_count': watched_count,
        'unwatched_count': unwatched_count,
        'average_rating': average_rating,
        'progress_percentage': progress_percentage,
        'top_rated': top_rated,
        'recently_added': recently_added,
        'genre_labels_json': json.dumps(genre_labels),
        'genre_data_json': json.dumps(genre_data),
        'earned_badges': earned_badges,
        'locked_badges': locked_badges
    }
    return render(request, 'movies/dashboard.html', context)

def upcoming_calendar(request):
    url = f"{BASE_URL}/movie/upcoming?api_key={settings.TMDB_API_KEY}&region=US&page=1"
    response = requests.get(url)
    movies = response.json().get('results', [])
    
    url2 = f"{BASE_URL}/movie/upcoming?api_key={settings.TMDB_API_KEY}&region=US&page=2"
    response2 = requests.get(url2)
    movies.extend(response2.json().get('results', []))
    
    today = datetime.now().strftime('%Y-%m-%d')
    upcoming_movies = [m for m in movies if m.get('release_date') and m['release_date'] > today]
    
    # Remove duplicates if any
    seen = set()
    unique_upcoming = []
    for m in upcoming_movies:
        if m['id'] not in seen:
            unique_upcoming.append(m)
            seen.add(m['id'])
    
    unique_upcoming.sort(key=lambda x: x['release_date'])
    
    for m in unique_upcoming:
        try:
            date_obj = datetime.strptime(m['release_date'], '%Y-%m-%d')
            m['release_month'] = date_obj.strftime('%b').upper()
            m['release_day'] = date_obj.strftime('%d')
            m['release_year'] = date_obj.strftime('%Y')
        except ValueError:
            m['release_month'] = ''
            m['release_day'] = ''
            m['release_year'] = ''
            
    return render(request, 'movies/calendar.html', {'movies': unique_upcoming})

@login_required(login_url='/accounts/login/')
def movie_wrapped(request):
    user_id = request.user.id
    
    watched_movies = list(watchlist_collection.find({"user_id": user_id, "watched": True}))
    total_watched = len(watched_movies)
    total_hours = total_watched * 2 
    
    genre_counter = Counter()
    highest_rated = None
    max_rating = -1
    
    for m in watched_movies:
        if 'genres' in m and m['genres']:
            for g in m['genres']:
                genre_counter[g] += 1
                
        rating = m.get('rating', 0)
        if rating > max_rating:
            max_rating = rating
            highest_rated = m
            
    top_genre = genre_counter.most_common(1)[0][0] if genre_counter else "Unknown"
    
    context = {
        'total_watched': total_watched,
        'total_hours': total_hours,
        'top_genre': top_genre,
        'highest_rated': highest_rated,
    }
    
    return render(request, 'movies/wrapped.html', context)

@login_required(login_url='/accounts/login/')
def movie_diary(request):
    user_id = request.user.id
    
    # Fetch watched movies and sort by ObjectId descending (newest added to watchlist first)
    watched_movies_cursor = watchlist_collection.find({"user_id": user_id, "watched": True}).sort("_id", -1)
    watched_movies = list(watched_movies_cursor)
    
    return render(request, 'movies/diary.html', {'diary_entries': watched_movies})