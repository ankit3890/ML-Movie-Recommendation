from flask import Flask, request, jsonify
import pickle
import os
import requests
import random
# from dotenv import load_dotenv

# load_dotenv()


app = Flask(__name__)

# Note: Static files (index.html, CSS, JS) are served directly by Vercel from root
# This Flask app only handles /api/* routes


# Load models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Loading models...")
try:
    with open(os.path.join(BASE_DIR, 'tfidf_matrix.pkl'), 'rb') as f:
        tfidf_matrix = pickle.load(f)
    with open(os.path.join(BASE_DIR, 'indices_dict.pkl'), 'rb') as f:
        indices = pickle.load(f) # Now a dict
    with open(os.path.join(BASE_DIR, 'movies_list.pkl'), 'rb') as f:
        movies_list = pickle.load(f) # Now a list
    print("Models loaded successfully.")
    
    # Pre-compute titles list for faster suggestion lookups
    all_titles = list(indices.keys()) if indices is not None else []
    # Ensure all are strings just in case
    all_titles = [str(t) for t in all_titles]
except Exception as e:
    print(f"Error loading models: {e}")
    tfidf_matrix = None
    indices = {}
    movies_list = []
    all_titles = []

TMDB_API_KEY = "fcae52d0267055bc9cca73e252188a4b"
BASE_IMG_URL = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER_IMG = "https://via.placeholder.com/500x750?text=No+Image"

def get_tmdb_data(title):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data.get("results"):
            movie = data["results"][0]
            poster_path = movie.get("poster_path")
            poster_url = BASE_IMG_URL + poster_path if poster_path else PLACEHOLDER_IMG
            return {
                "id": movie.get("id"),
                "poster": poster_url,
                "title": movie.get("title", title), # Use TMDB official title
                "overview": movie.get("overview", "")
            }
    except Exception as e:
        print(f"Error fetching data for {title}: {e}")
    
    return {
        "id": None,
        "poster": PLACEHOLDER_IMG,
        "title": title,
        "overview": ""
    }

@app.route('/api/movie/<int:movie_id>')
def movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "append_to_response": "videos"
        }
        r = requests.get(url, params=params).json()

        trailer = None
        for v in r.get("videos", {}).get("results", []):
            if v["site"] == "YouTube" and v["type"] == "Trailer":
                trailer = f"https://www.youtube.com/watch?v={v['key']}"
                break

        return jsonify({
            "title": r.get("title"),
            "overview": r.get("overview"),
            "poster": f"https://image.tmdb.org/t/p/w500{r['poster_path']}" if r.get("poster_path") else None,
            "rating": r.get("vote_average"),
            "release_date": r.get("release_date"),
            "runtime": r.get("runtime"),
            "genres": [g["name"] for g in r.get("genres", [])],
            "trailer": trailer
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    if not all_titles:
        return jsonify([])
    
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
        
    # Simple case-insensitive containment check
    # Limit to 5 results for speed and UI space
    matches = [t for t in all_titles if query in t.lower()][:5]
    
    return jsonify(matches)

@app.route('/api/random', methods=['GET'])
def get_random_movies():
    if not all_titles:
        return jsonify([])
    
    # Select 12 random movies
    num_to_select = min(len(all_titles), 12)
    random_titles = random.sample(all_titles, num_to_select)
    
    response_data = []
    for title in random_titles:
        tmdb_data = get_tmdb_data(title)
        if tmdb_data["id"]: # Only add if we found a valid movie ID
            response_data.append({
                "title": tmdb_data["title"],
                "poster": tmdb_data["poster"],
                "id": tmdb_data["id"]
            })
        
    return jsonify(response_data)

@app.route('/api/recommend', methods=['GET'])
def recommend():
    if movies_list is None:
        return jsonify({"error": "Model failed to load"}), 500

    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Case-insensitive lookup helper
    if title not in indices:
        title_lower = title.lower()
        matches = [t for t in all_titles if title_lower == str(t).lower()]
        if matches:
            idx = indices[matches[0]]
            title = matches[0] # Use correct casing found
        else:
            return jsonify({"error": "Movie not found", "recommendations": []}), 404
    else:
        idx = indices[title]

    try:
        # idx from dict is an integer
        
        # Calculate similarity using Scipy sparse dot product
        # tfidf_matrix is CSR, so dot usage:
        # matrix[idx] is 1xN sparse row
        # matrix.T is NxM sparse
        # Result is 1xM cosine similarity (since vectors are unit length from TfidfVectorizer)
        cosine_sim = tfidf_matrix[idx].dot(tfidf_matrix.T).toarray().flatten()
        
        # Get top 10
        # argsort sorts ascending, so we take from the end
        similar_idx = cosine_sim.argsort()[::-1][1:11]
        
        # Fetch posters and scores for recommendations
        response_data = []
        for i in similar_idx:
            movie_title = movies_list[i] # Access simplified list
            score = cosine_sim[i]
            match_percentage = int(round(score * 100))
            
            tmdb_data = get_tmdb_data(movie_title)
            
            if tmdb_data["id"]:
                 response_data.append({
                    "title": tmdb_data["title"],
                    "poster": tmdb_data["poster"],
                    "match": match_percentage,
                    "id": tmdb_data["id"] 
                })
        
        return jsonify({
            "movie": title,
            "recommendations": response_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
