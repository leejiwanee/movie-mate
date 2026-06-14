# 🎬 MovieMate

MovieMate is a Django-based web application that utilizes the TMDB API to discover trending movies, search for movies, and manage your personal Watchlist using MongoDB.

## 🌟 Features

- **🔥 Trending Movies:** Check out the current most popular movies.
- **🔍 Search Movies:** Search for your favorite movies based on the TMDB database.
- **⭐ Watchlist:** Save and manage movies you want to watch later. (Powered by MongoDB)
- **🍿 Tonight:** Get movie recommendations based on high ratings and popularity.

## 🛠 Tech Stack

- **Backend:** Python 3, Django 5.1
- **Database:** MongoDB (via `djongo` & `pymongo`)
- **API:** TMDB (The Movie Database) API

## ⚙️ Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd moviemate_prj
```

### 2. Set up virtual environment and install dependencies
This project uses the following libraries: `django`, `djongo`, `pymongo`, `python-dotenv`, `requests`.

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

pip install -r requirements.txt # (if requirements.txt is available)
# OR
pip install django djongo pymongo python-dotenv requests
```

### 3. Set Environment Variables (.env)
Create a `.env` file in the root directory of the project and provide the following variables:
```env
SECRET_KEY=your_django_secret_key
TMDB_API_KEY=your_tmdb_api_key
```
> [!NOTE]
> You can obtain a TMDB API key by signing up on the [official TMDB website](https://www.themoviedb.org/).

### 4. Run MongoDB
Ensure MongoDB is installed locally and running on `mongodb://localhost:27017/`.
The application will automatically create and use a database named `moviemate_db`.

### 5. Run the Server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your web browser to check out the application.

## 📂 Project Structure
- `moviemate_prj/`: Main Django project configuration folder (`settings.py`, `urls.py`)
- `movies/`: Core Django App handling trending, searching, watchlist, and recommendations
  - `views.py`: Core business logic, TMDB API calls, and MongoDB integration
  - `urls.py`: Internal URL routing for the `movies` app
