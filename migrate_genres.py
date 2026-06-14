import os
import sys
import django
import requests

sys.path.append('/Users/jiwanlee/Code/moviemate_prj')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviemate_prj.settings')
django.setup()

from movies.views import watchlist_collection
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"

def migrate():
    movies = watchlist_collection.find({"genres": {"$exists": False}})
    count = 0
    for movie in movies:
        movie_id = movie.get('movie_id')
        if not movie_id:
            continue
            
        try:
            url = f"{BASE_URL}/movie/{movie_id}?api_key={settings.TMDB_API_KEY}"
            response = requests.get(url)
            movie_data = response.json()
            if 'genres' in movie_data:
                genres = [g['name'] for g in movie_data['genres']]
                watchlist_collection.update_one(
                    {"_id": movie["_id"]},
                    {"$set": {"genres": genres}}
                )
                print(f"Updated {movie.get('title')} with genres: {genres}")
                count += 1
        except Exception as e:
            print(f"Failed for {movie.get('title')}: {e}")
            
    print(f"Migration complete. Updated {count} movies.")

if __name__ == '__main__':
    migrate()
