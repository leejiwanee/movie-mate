from pymongo import MongoClient
from django.http import JsonResponse, render
from django.views.decorators.csrf import csrf_exempt

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