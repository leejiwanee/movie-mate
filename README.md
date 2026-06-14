# 🎬 MovieMate (Premium Edition)

MovieMate is a modern, premium Django-based web application that utilizes the TMDB API to discover trending movies, search for movies, and securely manage your personal Watchlist using MongoDB.

## ✨ Project Results & UI Showcase
Here are the recent major upgrades applied to the project:
- **Premium SaaS Aesthetic**: A sleek, modern user interface with soft drop shadows, glassmorphism navbars, and professional Indigo styling.
- **AJAX & Toast Notifications**: Adding/removing movies happens instantly in the background without page reloads, displaying elegant sliding Toast popups.
- **Personalized Accounts**: Full Authentication system where each user gets their own private Watchlist.

*(You can add your own screenshots here! For example:)*
> ![Home Page Screenshot](/path/to/your/screenshot.png)
> ![Watchlist with Toasts](/path/to/your/screenshot2.png)

## 🌟 Features

- **🛡️ Secure Authentication:** Sign up, log in, and manage your private session.
- **🔥 Trending Movies:** Check out the current most popular movies worldwide.
- **🔍 Search Movies:** Search for your favorite movies across the vast TMDB database.
- **⭐ Private Watchlist:** Save movies, view posters, mark them as "Watched/Unwatched", or remove them from your personal list.
- **🍿 Tonight:** Get highly-rated movie recommendations instantly.

## 🛠 Tech Stack

- **Backend:** Python 3, Django 5.1
- **Database:** 
  - **SQLite:** For robust User Authentication & Sessions.
  - **MongoDB:** (via `pymongo`) For fast, flexible Watchlist document storage.
- **API:** TMDB (The Movie Database) API
- **Frontend:** Vanilla JS (`fetch` API), Custom Premium CSS (No external frameworks)

## ⚙️ Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd moviemate_prj
```

### 2. Set up virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
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
python manage.py migrate  # Creates auth tables in SQLite
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your web browser.

## 📂 Project Structure
- `moviemate_prj/`: Main Django project configuration folder
- `accounts/`: App handling User Authentication (Login, Register, Logout)
- `movies/`: Core Django App handling trending, searching, AJAX views, and MongoDB integration
