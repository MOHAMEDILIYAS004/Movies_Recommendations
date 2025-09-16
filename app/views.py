from django.shortcuts import render
import requests

TMDB_API_KEY = "7f3b4f32babdf795350ecd27f6a18cb3"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_DETAIL_URL = "https://api.themoviedb.org/3/movie/{}"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# Fetch genres from TMDB (to map genre_ids → names)
def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {genre["id"]: genre["name"] for genre in data["genres"]}
    return {}

GENRE_MAP = get_genres()

def movie_search(request):
    query = request.GET.get('q', '')
    movies = []

    if query:
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "language": "en-US",
            "page": 1,
            "include_adult": False
        }
        response = requests.get(TMDB_SEARCH_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            for movie in data.get('results', []):
                genres = [GENRE_MAP.get(gid, "") for gid in movie.get('genre_ids', [])]
                movies.append({
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'poster': TMDB_IMAGE_BASE + movie['poster_path'] if movie.get('poster_path') else None,
                    'release_date': movie.get('release_date'),
                    'overview': movie.get('overview'),
                    'rating': movie.get('vote_average'),
                    'genres': ", ".join(genres),
                })

    return render(request, 'app/movie_search.html', {'movies': movies, 'query': query})


def movie_detail(request, movie_id):
    url = TMDB_DETAIL_URL.format(movie_id)
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    movie = {}
    if response.status_code == 200:
        data = response.json()
        movie = {
            'title': data.get('title'),
            'poster': TMDB_IMAGE_BASE + data['poster_path'] if data.get('poster_path') else None,
            'release_date': data.get('release_date'),
            'overview': data.get('overview'),
            'rating': data.get('vote_average'),
            'genres': ", ".join([g["name"] for g in data.get("genres", [])]),
            'runtime': data.get('runtime'),
            'tagline': data.get('tagline'),
        }

    return render(request, 'app/movie_detail.html', {'movie': movie})
